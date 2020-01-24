#!/usr/bin/env bash

# If necessary run "make git-server-init" in the project root directory
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
SOURCE=$(git config --get remote.origin.url)
BRANCH=$(git symbolic-ref -q --short HEAD)
VCS_REF=$(git rev-parse HEAD)

COMMAND=$1
PARAMS="${@:2}"
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
        docker-compose --project-name dev -f docker-compose.yml -f docker-compose.dev.yml up -d ${PARAMS}
        ;;
    up-prod)
        docker-compose --project-name prod -f docker-compose.yml -f docker-compose.prod.yml up -d ${PARAMS}
        ;;
    down-dev)
        docker-compose --project-name dev -f docker-compose.yml -f docker-compose.dev.yml down ${PARAMS}
        ;;
    down-prod)
        docker-compose --project-name prod -f docker-compose.yml -f docker-compose.prod.yml down ${PARAMS}
        ;;
    *)
        echo $"Usage: $0 {build-dev|up-dev|down-dev}"
        exit 1
esac
