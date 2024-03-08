#!/bin/sh

# Run migrations after the container starts
alembic upgrade head

# Start your FastAPI application
exec "$@"
