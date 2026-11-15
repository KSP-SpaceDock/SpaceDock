#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until docker compose exec -T db pg_isready -U postgres -q 2>/dev/null; do
    sleep 1
done

echo "Initializing database..."
docker compose exec -T backend python scripts/db_init.py

echo "Database initialized."
