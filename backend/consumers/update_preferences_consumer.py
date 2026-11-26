from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import logging
import json
import os
import time
from codegen import recommendation_service_pb2 as rec_pb2

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')


class _NoopContext:
    """Stands in for a gRPC context when the recommendation service is called
    directly (not through a gRPC request)."""

    def set_code(self, code):
        pass

    def set_details(self, details):
        pass


def _connect(retries=10, delay_seconds=3):
    """Create the consumer, waiting for Kafka to come up if it is not ready yet."""
    for attempt in range(1, retries + 1):
        try:
            return KafkaConsumer(
                'preferences_update',  # Topic name
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id='recommendation-service-group',  # Consumer group ID
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))  # Deserialize message
            )
        except NoBrokersAvailable:
            logging.warning(
                f"Kafka not reachable at {KAFKA_BOOTSTRAP_SERVERS} "
                f"(attempt {attempt}/{retries})"
            )
            time.sleep(delay_seconds)
    raise NoBrokersAvailable(f"Could not reach Kafka at {KAFKA_BOOTSTRAP_SERVERS}")


def start_kafka_consumer(redis_client, db, recommendation_service):
    """
    Starts a Kafka consumer to process user preference updates.
    """
    logging.info("Starting Kafka consumer for preferences_update...")
    consumer = _connect()

    for message in consumer:
        try:
            logging.info(f"Received message from Kafka: {message.value}")
            process_preference_updates(message.value, redis_client, db, recommendation_service)
        except Exception as e:
            logging.error(f"Error processing Kafka message: {str(e)}")


def process_preference_updates(message, redis_client, db, recommendation_service):
    """
    Processes a single Kafka message for updating user preferences.
    """
    user_id = message.get("user_id")
    preferences = message.get("preferences")

    if not user_id or not preferences:
        logging.error("Invalid Kafka message format. Missing 'user_id' or 'preferences'.")
        return

    logging.info(f"Processing preference update for user_id: {user_id}, preferences: {preferences}")

    try:
        # Update the database
        preferences_json = json.dumps(preferences)
        query = "UPDATE Users SET preferences = %s WHERE id = %s"
        db.execute(query, (preferences_json, user_id))
        logging.info(f"Preferences updated in the database for user_id {user_id}.")

        # Invalidate cache
        cache_key = f"recommendations:{' '.join(preferences['category']).lower()}:{preferences['city'].lower()}"
        if redis_client:
            redis_client.delete(cache_key)
            logging.info(f"Invalidated cache for key: {cache_key}")

        # Fetch new recommendations. GetRecommendations stores them in the cache
        # under the same key when it computes them.
        rec_request = rec_pb2.RecommendationRequest(
            category=preferences["category"],
            city=preferences["city"]
        )
        response = recommendation_service.GetRecommendations(rec_request, _NoopContext())

        # Cache new recommendations
        recommendations = [
            {
                "name": rec.name,
                "category": rec.category,
                "rating": rec.rating,
                "review_count": rec.review_count,
                "city": rec.city,
                "address": rec.address,
                "phone": rec.phone,
                "price": rec.price,
                "image_url": rec.image_url,
                "url": rec.url,
            }
            for rec in response.recommendations
        ]
        serialized_recommendations = json.dumps(recommendations)
        if redis_client:
            redis_client.set(cache_key, serialized_recommendations, ex=3600)
            logging.info(f"Cached new recommendations for key: {cache_key}")

    except Exception as e:
        logging.error(f"Error processing preference update for user_id {user_id}: {str(e)}")
