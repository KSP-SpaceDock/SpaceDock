#!/bin/bash
set -e

# works inside SpaceDock folder on alpha/beta, which is a venv
bin/pip3 install --no-cache-dir -U -r requirements.txt

./build-frontend.sh

# Get $worker-count from config.ini
worker_count=$(/usr/bin/awk -F= '/^worker-count/{print $2}' config.ini)
# Write it into a temporary env file which is read by the services
echo "worker_count=${worker_count}" > systemd/spacedock@.env
