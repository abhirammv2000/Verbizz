# Verbizz - Personalized Business Recommendation System

Verbizz is a scalable, cloud-based platform designed to deliver personalized business recommendations. This project leverages modern technologies like Flask, gRPC, Redis, Kafka, PostgreSQL, and Kubernetes to provide a seamless user experience for updating preferences and receiving recommendations in real-time.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [System Architecture](#system-architecture)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Data Directory](#data-directory)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)

## Project Overview
Verbizz allows users to:
- Update their preferences (e.g., categories and city).
- View personalized business recommendations.
- Experience real-time updates powered by Kafka.

The project is built on a microservices architecture, ensuring scalability, reliability, and performance.

## Features
- **User-Friendly Interface**: Simple and interactive UI for updating preferences and receiving recommendations.
- **Preference Updates over Kafka**: when a user changes their preferences, the frontend publishes a message to Kafka and a consumer in the backend refreshes the cached recommendations.
- **Fast Performance**: Redis caching reduces latency and enhances user experience.
- **Scalability**: Kubernetes orchestrates microservices for seamless scaling.
- **Secure Storage**: PostgreSQL stores user profiles and business data securely.

## Technologies Used
### Backend
- Python with **gRPC** (business logic and API services)
- **PostgreSQL** (database)
- **Redis** (caching)
- **Apache Kafka** (messaging)
- **Kubernetes** and **Docker** (container orchestration)

### Frontend
- **Flask** (web application)
- HTML/CSS/JavaScript with Bootstrap for responsive design

### Other Tools
- Python `logging` for debugging
- `backend/client.py`, a manual script that calls the gRPC services (there is no automated test suite yet)

## System Architecture
![System Architecture](Images/sys_arch.jpeg)

## Application Screenshots

Below are screenshots showcasing the key features of the Verbizz application:

### 1. **Register**
   - **Description**: The registration page allows new users to create an account by providing their email, password, name, preferences (categories), and city.
   - **Screenshot**:  
     ![Register](Images/register.png)

### 2. **Login**
   - **Description**: The login page enables existing users to securely access their accounts using their email and password.
   - **Screenshot**:  
     ![Login](Images/login.png)

### 3. **Recommendations**
   - **Description**: The recommendations page displays personalized business suggestions based on user preferences, such as category and city.
   - **Screenshot**:  
     ![Recommendations](Images/recommend.png)

### 4. **Update Preferences**
   - **Description**: The update preferences page allows users to modify their preferences for categories and city, dynamically updating the recommendations.
   - **Screenshot**:  
     ![Update Preferences](Images/update_pref.png)
## Installation

### Quick start with Docker Compose
This starts PostgreSQL (with the business data loaded), Redis, Kafka, the gRPC backend and the Flask frontend. You only need Docker.

```bash
git clone https://github.com/abhirammv2000/Verbizz.git
cd Verbizz
cp .env.example .env        # then edit .env and set the three secrets
docker compose up --build
```

Open http://localhost:5000, register with a few categories (for example `Gyms`) and a city that is in the data (for example `Austin`), and you should see recommendations. The first start loads about 11,000 businesses into PostgreSQL, so it takes a little longer. `docker compose down -v` removes the database volume.

### Running the pieces by hand
Use this if you want to run the Python code outside Docker. You then need PostgreSQL (with the `cube` and `earthdistance` extensions), Redis and Kafka running yourself. Copy `backend/.env.example` to `backend/.env` and adjust the hosts.

#### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- Kafka
- Docker and Kubernetes (for containerization and orchestration)

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/abhirammv2000/Verbizz.git
   ```
2. Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
3. Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Start the backend server:
    ```bash
    python server.py
    ```

### Frontend Setup
1. Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2. Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Start the Flask app:
    ```bash
    flask run
    ```
## Data Directory

The `data` directory contains essential files for recommendations. Below is a description of its contents:

### Contents
1. **`final_cleaned_data.csv`**:
   - **Description**: Preprocessed and cleaned data used for generating recommendations.
   - **Purpose**: Provides structured data input for the recommendation engine.

2. **`full_data.pkl`**:
   - **Description**: Serialized file containing the full dataset.
   - **Purpose**: Used for training and testing the recommendation model.

3. **`tfidf_vectorizer.pkl`**:
   - **Description**: Pre-trained TF-IDF vectorizer model.
   - **Purpose**: Extracts features from textual data for content-based recommendations.
  
- These files are required for backend services and must not be modified unless re-training or re-processing is performed.
- Ensure these files are accessible to the backend during execution.

## Usage
1. Navigate to the frontend URL (default: `http://127.0.0.1:5000`).
2. Register or log in to your account.
3. Update your preferences (categories and city).
4. View personalized recommendations based on your preferences.

## Known Limitations
- **Login tokens are not checked.** `LoginUser` returns a JWT, but no RPC verifies it. The frontend keeps the user in a signed Flask session instead.
- **Database errors are swallowed.** `backend/db/db.py` prints the error and returns `None`, so for example registering an email that already exists reports success without inserting anything. It also shares one connection and cursor across the gRPC worker threads.
- **The "new business" Kafka path does nothing.** `AddBusiness` publishes to `new-business-data`, but nothing starts the consumer in `backend/consumers/business_consumer.py`. Recommendations come from the pickled dataset in `data/`, not from the PostgreSQL `Business` table, so a newly added business is not recommended.
- **Recommendations use category text only.** Ratings, review counts and price do not affect the ranking.
- **The Kubernetes files are not tested.** `postgres-deployment.yaml` mounts a `hostPath` from the original author's machine, and the image in `grpc-server-deployment.yaml` is `dkiran760/grpc-server`. `deploy-all.sh` now creates the secrets from environment variables (`POSTGRES_PASSWORD`, `JWT_SECRET_KEY`), but it has not been run against a cluster. `clean-k8s.sh` deletes everything in the current namespace, so check your `kubectl` context before running it.
- **Old secrets are still in git history.** Earlier commits contain a committed `.env` and a Postgres password. Treat those values as exposed and do not reuse them.

## Future Enhancements
- Integrate advanced machine learning models for more accurate recommendations.
- Enhance UI/UX for a richer user experience.
- Add support for multilingual recommendations.
- Implement detailed analytics and reporting features. 
---
For any queries or contributions, please contact Kiran Devihosur at kirandevihosur74@gmail.com  
Happy coding! 🎉
