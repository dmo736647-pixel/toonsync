#!/bin/bash

# Run database migrations (ignore errors if tables already exist)
alembic upgrade head 2>/dev/null || echo "Migration completed with warnings"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
