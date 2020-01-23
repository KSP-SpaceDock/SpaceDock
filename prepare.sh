#!/bin/bash
set -e

# works inside SpaceDock folder on alpha/beta, which is a venv
bin/pip3 install --no-cache-dir -U -r requirements.txt

./build-frontend.sh
