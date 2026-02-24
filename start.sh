#!/bin/bash

echo "Starting deployment..."

# Run database migrations (ignore all errors)
echo "Running database migrations..."
alembic upgrade head || true

echo "Starting application..."
# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
