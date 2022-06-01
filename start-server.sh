#!/bin/bash
set -e

# Create default config files, if needed
test -f config.ini || cp config.ini.example config.ini
test -f alembic.ini || cp alembic.ini.example alembic.ini
test -f logging.ini || cp logging.ini.example logging.ini

case "$OSTYPE" in
    linux*)
        # Only start docker service on Linux
        # (pgrep and systemctl may not be available elsewhere)
        if [[ -z "$(pgrep dockerd)" ]];
        then
            systemctl start docker.service
        fi
        ;;
    msys | cygwin)
        # Turn off db's volume mounting because we can't make the owners match,
        # by mounting it at /var/lib/postgresql/data_dummy instead.
        # The db will not persist between restarts, but that's better than
        # failing to start and can still be used to investigate some issues.
        echo 'Windows OS detected, disabling db volume mounting.'
        echo 'NOTE: Database will NOT persist across restarts!'
        echo
        export DISABLE_DB_VOLUME=_dummy
        ;;
esac

COMPOSE_FILE="docker-compose.yml"
[ "$1" == "prod" ] && COMPOSE_FILE="docker-compose-prod.yml"

# build containers
docker-compose -f "${COMPOSE_FILE}" build

# start database server
docker-compose -f "${COMPOSE_FILE}" up -d db

# stop existing backend
docker-compose -f "${COMPOSE_FILE}" stop backend

# wait for it to accept connections, then create/migrate db schema
source .env
docker-compose -f "${COMPOSE_FILE}" run --rm --no-deps \
-e CONNECTION_STRING="${CONNECTION_STRING}" \
backend bash -c '''
set -e
spacedock database wait &&
spacedock database initialize &&
spacedock database migrate &&
spacedock database populate
'''

# start other containers
docker-compose -f "${COMPOSE_FILE}" up -d
