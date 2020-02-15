#!/usr/bin/env bash
# Script for working with the main docker-compose commands.
# When building an image, git attributes are written to environment variables

# Example usage:
#  base:
#   ./docker-compose.sh build-dev
#   ./docker-compose.sh up-dev DL1 faceembedder
#   ./docker-compose.sh down-dev DL1
#  extended options:
#   ./docker-compose.sh build-dev --parallel --force-rm
#   ./docker-compose.sh up-dev DL1 faceembedder --no-color --build
#   ./docker-compose.sh down-dev DL1 -v --rmi


# If necessary run "make git-server-init" in the project root directory
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
SOURCE=$(git config --get remote.origin.url)
BRANCH=$(git symbolic-ref -q --short HEAD)
VCS_REF=$(git rev-parse HEAD)

COMMAND=$1
SERVER=$2
PARAMS="${@:3}"
case ${COMMAND} in
    build-dev)
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml build \
            --build-arg BUILD_DATE=${BUILD_DATE} \
            --build-arg SOURCE=${SOURCE} \
            --build-arg BRANCH=${BRANCH} \
            --build-arg VCS_REF=${VCS_REF} \
            ${PARAMS}
        ;;
    build-prod)
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml build \
            --build-arg BUILD_DATE=${BUILD_DATE} \
            --build-arg SOURCE=${SOURCE} \
            --build-arg BRANCH=${BRANCH} \
            --build-arg VCS_REF=${VCS_REF} \
            ${PARAMS}
        ;;
    up-dev)
         docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.${SERVER,,}.yml \
            --project-name dev \
            up -d ${PARAMS}
        ;;
    up-prod)
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.${SERVER,,}.yml \
            --project-name prod \
            up -d ${PARAMS}
        ;;
    down-dev)
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.${SERVER,,}.yml \
            --project-name dev \
            down ${PARAMS}
        ;;
    down-prod)
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.${SERVER,,}.yml \
            --project-name prod \
            down ${PARAMS}
        ;;
    *)
        echo $"Usage: $0 {build-dev|up-dev|down-dev}"
        exit 1
esac
