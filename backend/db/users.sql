-- Users table used by UserService. It was missing from the repo: init.sql only created Business.
-- Column names match the queries in backend/services/user/user_service.py.
CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    preferences JSONB,
    preferences_collected BOOLEAN NOT NULL DEFAULT FALSE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
