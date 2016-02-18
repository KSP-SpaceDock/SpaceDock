#!/bin/bash -x

# Copy over the config files, if needed
test -f /opt/spacedock/config.ini || cp /opt/spacedock/config.ini.example /opt/spacedock/config.ini
test -f /opt/spacedock/alembic.ini || cp /opt/spacedock/alembic.ini.example /opt/spacedock/alembic.ini

# TODO: I don't like doing this. It seems like there should be a cleaner way to get all this information loaded into the postgres container.
DB_HOST="db"
DB_PORT="5432"
DB_USER="postgres"
DB_NAME="kerbalstuff"

# Assume we are starting with a good DB.
FRESH_DB=false

# Wait for db to be alive and accepting connections
until nc -z $DB_HOST $DB_PORT
do
    echo "Waiting for db to be alive"
    sleep 0.5
done

# Create the kerbalstuff database if it doesn't exist.
if [[ $(psql -h $DB_HOST -U $DB_USER -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'") != "1" ]]; then
    createdb -h $DB_HOST -U $DB_USER $DB_NAME
    FRESH_DB=true
fi

# Make sure that we are at the latest version of the scheme.
# It's my assumption that this is an idempotent command and I can freely run it over and over without consequence.
/venv/spacedock/bin/python -c 'from alembic.config import Config; from alembic import command; alembic_cfg = Config("alembic.ini"); command.stamp(alembic_cfg, "head"); exit()' && \
/venv/spacedock/bin/alembic upgrade head

if [[ "$FRESH_DB" == true ]]; then
    # Add a default admin user for development.
    /venv/spacedock/bin/python -c 'from KerbalStuff.objects import *; from KerbalStuff.database import db; u = User("admin", "admin@example.com", "development"); u.admin = True; u.confirmation = None; db.add(u); db.commit()'

    # Add a default test user for development.
    /venv/spacedock/bin/python -c 'from KerbalStuff.objects import *; from KerbalStuff.database import db; u = User("user", "user@example.com", "development"); u.confirmation = None; db.add(u); db.commit()'
fi

# Start the app
/venv/spacedock/bin/python /opt/spacedock/app.py
