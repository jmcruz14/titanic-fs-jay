-- Create database if it doesn't exist
SELECT 'CREATE DATABASE titanicdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'titanicdb')\gexec

-- Connect to the database
\c titanicdb

-- Create your tables here
CREATE TABLE IF NOT EXISTS passengers (
    id SERIAL PRIMARY KEY,
    passenger_id INTEGER,
    survived INTEGER,
    pclass INTEGER,
    name VARCHAR(255),
    sex VARCHAR(10),
    age FLOAT,
    sibsp INTEGER,
    parch INTEGER,
    ticket VARCHAR(50),
    fare FLOAT,
    cabin VARCHAR(50),
    embarked VARCHAR(10)
);

CREATE INDEX IF NOT EXISTS idx_passenger_id ON passengers(passenger_id);