#!/bin/bash
set -e

# Run database migrations
alembic upgrade head 2>/dev/null || true

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
