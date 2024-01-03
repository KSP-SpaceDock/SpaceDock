#!/usr/bin/env bash
set -e

case "$OSTYPE" in
    linux*)
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

docker-compose build backend

docker-compose up -d db

source .env
docker-compose run --rm --no-deps -u root \
  -e CONNECTION_STRING="${CONNECTION_STRING}" \
  backend bash -c """
set -e
spacedock database wait &&
alembic revision --autogenerate -m \"$(date +%Y_%m_%d-%H_%M_%S)\" &&
chmod g+rw alembic/versions/* &&
alembic history --verbose
"""

case "$OSTYPE" in
    linux*)
        sudo chown "${USER}":"${USER}" alembic/versions/*
        ;;
    msys | cygwin)
        ;;
esac
