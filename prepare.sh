#!/bin/bash
# Compares the current git HEAD with the one of the previous deployment.
# If it is the same, install the same requirements version as last time.
# If it differs, upgrade all packages to the latest version.

set -e

if [[ -f .last_head ]]; then
    LAST_HEAD=$(cat .last_head)
else
    LAST_HEAD=""
fi

HEAD=$(git rev-parse HEAD)

# Make sure we've got the latest pip, to benefit of security and relationship resolver fixes.
bin/pip3 install -U pip

if [[ "$LAST_HEAD" != "$HEAD" || ! -f .frozen-requirements.txt ]]; then
  echo "HEAD at last deployment: $LAST_HEAD - Current HEAD: $HEAD"
  # works inside SpaceDock folder on alpha/beta, which is a venv
  bin/pip3 install --no-cache-dir -U -r requirements.txt
  bin/pip3 freeze > .frozen-requirements.txt

  # Frontend only needs to be rebuilt if the commit changed
  ./build-frontend.sh
else
  bin/pip3 install --no-cache-dir -r .frozen-requirements.txt
fi

echo "$HEAD" > .last_head
