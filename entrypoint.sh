#!/bin/bash
set -e

echo "Starting entrypoint script..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h postgres -p 5432 -U bot_user; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
python init_db.py

# Seed database with existing data
echo "Seeding database with existing data..."
python seed_database.py

echo "Starting the bot application..."
exec python app.py
