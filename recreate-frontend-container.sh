#!/bin/bash
docker compose down
docker compose build --no-cache frontend
docker compose up -d --force-recreate frontend