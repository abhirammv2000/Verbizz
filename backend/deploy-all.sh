#!/bin/bash
set -e

# Secrets come from the environment, not from files in the repository.
#   export POSTGRES_PASSWORD=... JWT_SECRET_KEY=...
: "${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD before running this script}"
: "${JWT_SECRET_KEY:?Set JWT_SECRET_KEY before running this script}"

kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic app-secrets \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# Init scripts that the Postgres deployment mounts (extensions, tables, CSV load).
kubectl create configmap postgres-init-scripts \
  --from-file=00_extensions.sql=db/00_extensions.sql \
  --from-file=10_business.sql=db/init.sql \
  --from-file=20_users.sql=db/users.sql \
  --from-file=30_after_load.sql=db/after_load.sql \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy the gRPC server service
kubectl apply -f grpc-server-deployment.yaml --validate=false

# Deploy Redis service
kubectl apply -f redis/redis_deployment.yaml --validate=false

# Deploy Kafka service
kubectl apply -f kafka/kafka_deployment.yaml --validate=false

# Deploy Postgres service
kubectl apply -f db/postgres-deployment.yaml --validate=false
kubectl apply -f db/postgres-pvc.yaml --validate=false
kubectl apply -f db/postgres-backup-cronjob.yaml --validate=false

echo "All deployments applied successfully!"
