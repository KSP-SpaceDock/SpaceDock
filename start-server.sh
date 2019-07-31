#!/bin/bash
set -e

# Create default config files, if needed
test -f config.ini || cp config.ini.example config.ini
test -f alembic.ini || cp alembic.ini.example alembic.ini

# start the docker
if [[ -z "$(pgrep dockerd)" ]];
then
    systemctl start docker.service
fi

COMPOSE_FILE="docker-compose.yml"
[ "$1" == "prod" ] && COMPOSE_FILE="docker-compose-prod.yml"

# stop existing instances
docker-compose -f "${COMPOSE_FILE}" down

# build containers
docker-compose -f "${COMPOSE_FILE}" build

# start database server
docker-compose -f "${COMPOSE_FILE}" up -d db

# wait for it to accept connections, then create/migrate db schema
source .env
docker-compose -f "${COMPOSE_FILE}" run --rm --no-deps \
-e CONNECTION_STRING="${CONNECTION_STRING}" \
backend bash -c '''
set -e
spacedock database wait &&
spacedock database initialize &&
spacedock database populate &&
spacedock database migrate
'''

# start other containers
docker-compose -f "${COMPOSE_FILE}" up -d