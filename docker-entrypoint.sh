#!/bin/bash
set -e

echo "🚀 Starting Vampires Bot Docker container..."

# Wait for database to be ready (if using external database)
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "⏳ Waiting for database to be ready..."
    
    # Extract database connection details
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
        until nc -z $DB_HOST $DB_PORT; do
            echo "Waiting for database at $DB_HOST:$DB_PORT..."
            sleep 2
        done
        echo "✅ Database is ready!"
    fi
fi

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Check if migrations were successful
if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully!"
else
    echo "❌ Database migrations failed!"
    exit 1
fi

# Start the application
echo "🤖 Starting bot application..."
exec "$@"
