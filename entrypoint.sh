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

# Seed database with actual data using direct migration
echo "Seeding database with actual data using direct migration..."
python seed_direct.py

# Alternative seeding options:
# python seed_database.py      # Sample data for development
# python seed_from_sql.py      # SQL dump method (if SQL dump exists)

echo "Starting the bot application..."
exec python app.py
