#!/bin/bash
set -e

source .env
STATIC=$(readlink -f ${STATIC_PATH})
rm -rf "${STATIC}"
mkdir "${STATIC}"

pushd frontend
export NPM_CONFIG_USERCONFIG=.npmrc
npm install
npm run build

pushd static
cp -rfv css/* "${STATIC}"
cp -rfv js/* "${STATIC}"
cp -rfv fonts/* "${STATIC}"
cp -rfv images/* "${STATIC}"
popd

cp -rfv build/* "${STATIC}"
