#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
until pg_isready -h postgres -p 5432 -U telegram_user -d telegram_news; do
  echo "Database is not ready yet. Waiting..."
  sleep 2
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
exec python3 api.py
