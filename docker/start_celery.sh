#!/bin/bash

$(cd dirname $0/..; C_FORCE_ROOT=true /venv/spacedock/bin/celery -A KerbalStuff.celery worker --loglevel=info)
