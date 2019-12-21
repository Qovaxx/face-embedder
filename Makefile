# Docker building settings
IMAGE_NAME=qovaxx/face-embedder
CONTAINER_NAME=face-embedder

TARGET="dev"
CONTAINER_PROJECT_DIRPATH=/project
BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%S%:z")
SOURCE=$(shell git config --get remote.origin.url)
BRANCH=$(shell git symbolic-ref -q --short HEAD)
VCS_REF=$(shell git rev-parse HEAD)
DOCKER_USER_NAME="root"
DOCKER_USER_PASS="pass"
DOCKER_SSH_PORT=22
HOST_SSH_PORT=9990

# Port forwarding settings
REMOTE_SSH_USER="qovaxx"
LOCAL_PORT=9990

# Help
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build:  ## Build the container
	DOCKER_BUILDKIT=1 nvidia-docker build \
	--tag ${IMAGE_NAME} \
	--file ./docker/Dockerfile \
	--target ${TARGET} \
	--build-arg BUILD_DATE=${BUILD_DATE} \
	--build-arg SOURCE=${SOURCE} \
	--build-arg BRANCH=${BRANCH} \
	--build-arg VCS_REF=${VCS_REF} \
	--build-arg PROJECT_DIRPATH=${CONTAINER_PROJECT_DIRPATH} \
	--build-arg DOCKER_USER_NAME=${DOCKER_USER_NAME} \
	--build-arg DOCKER_USER_PASS=${DOCKER_USER_PASS} \
	--build-arg DOCKER_SSH_PORT=${DOCKER_SSH_PORT} \
	.

run-dl1: ## Run container in dl1
	nvidia-docker run \
		-itd \
		--name=${CONTAINER_NAME} \
		--ipc=host \
		-e DISPLAY=unix${DISPLAY} \
		-v /tmp/.X11-unix:/tmp/.X11-unix --privileged \
		-v $(shell pwd):${CONTAINER_PROJECT_DIRPATH} \
		-p ${HOST_SSH_PORT}:${DOCKER_SSH_PORT} \
		${IMAGE_NAME}

exec: ## Run a bash in a running container
	nvidia-docker exec -it ${CONTAINER_NAME} bash

stop-rm: ## Stop and remove a running container
	docker stop ${CONTAINER_NAME}; docker rm ${CONTAINER_NAME}



up-dl1-docker-tunnel: ## Up a direct tunnel to the ssh port in the dl1 docker container
	bash port_forwarding.sh --name=dl1-docker-forwarding \
	--local-addr=localhost --local-port=${LOCAL_PORT} --remote-addr=localhost --remote-port=${HOST_SSH_PORT} \
	--remote-ssh=dl1 --ssh-user=${REMOTE_SSH_USER} --command=start

down-dl1-docker-tunnel: ## Shut down a direct tunnel to the dl1 docker
	bash port_forwarding.sh --name=dl1-docker-forwarding \
	 --local-addr=localhost --local-port=${LOCAL_PORT} --remote-addr=localhost --remote-port=${HOST_SSH_PORT} \
	 --remote-ssh=dl1 --ssh-user=${REMOTE_SSH_USER} --command=stop