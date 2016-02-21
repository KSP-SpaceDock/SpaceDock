#!/bin/bash -x

# Copy over the config files, if needed
test -f /opt/spacedock/config.ini || cp /opt/spacedock/config.ini.example /opt/spacedock/config.ini
test -f /opt/spacedock/alembic.ini || cp /opt/spacedock/alembic.ini.example /opt/spacedock/alembic.ini

# Wait for db to be alive and accepting connections
until nc -z db 5432
do
    echo "Waiting for db to be alive"
    sleep 0.5
done

# Initialize db
/venv/spacedock/bin/python /opt/spacedock/db_initialize.py

# Start the app
/venv/spacedock/bin/gunicorn app:app --config /opt/spacedock/docker/gunicorn.py
