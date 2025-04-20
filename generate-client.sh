#!/bin/sh -xe
rm -rf spotify-api
uvx openapi-generator-cli[jdk4py] generate \
    -g python \
    -i https://raw.githubusercontent.com/sonallux/spotify-web-api/refs/heads/main/fixed-spotify-open-api.yml \
    -o spotify-api \
    --remove-operation-id-prefix \
    -p projectName=spotify-api,packageName=spotify_api,library=asyncio
