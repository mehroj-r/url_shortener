#!/bin/sh
set -e

# Postgres readiness is handled by the compose healthcheck (depends_on: service_healthy)

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
