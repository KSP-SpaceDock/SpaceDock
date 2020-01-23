#!/usr/bin/env bash
set -e

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

sudo chown "${USER}":"${USER}" alembic/versions/*
