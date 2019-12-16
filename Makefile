IMAGE_NAME=qovaxx/face-embedder
CONTAINER_NAME=face-embedder

CONTAINER_PROJECT_DIRPATH=/face-embedder

BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%S%:z")
SOURCE=$(shell git config --get remote.origin.url)
BRANCH=$(shell git symbolic-ref -q --short HEAD)
VCS_REF=$(shell git rev-parse HEAD)

# HELP
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build:  ## Build the container
	nvidia-docker build \
	--tag ${IMAGE_NAME} \
	--file ./docker/Dockerfile.dev \
	--build-arg BUILD_DATE=${BUILD_DATE} \
	--build-arg SOURCE=${SOURCE} \
	--build-arg BRANCH=${BRANCH} \
	--build-arg VCS_REF=${VCS_REF} \
	.

exec: ## Run a bash in a running container
	nvidia-docker exec -it ${CONTAINER_NAME} bash

stop: ## Stop and remove a running container
	docker stop ${CONTAINER_NAME}; docker rm ${CONTAINER_NAME}
