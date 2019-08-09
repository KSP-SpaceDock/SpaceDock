#!/usr/bin/env bash
set -e

sudo systemctl daemon-reload
sudo systemctl restart spacedock.target
