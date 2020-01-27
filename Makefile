# Git settings
GIT_PROJECT_URL=https://gitlab.x5.ru/computer-vision/face-embedder
GIT_WORKING_BRANCH=feature/initial-changes


# There must be no space between the function name and the input argument
# Example: $(call env_arg,NAME))
#                        ^
define env_arg
	$(shell grep -oP '^$(1)=\K.*' .env)
endef

# Help
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

git-server-init: ## Initializing the repository to use the git metadata in the docker
	git init
	git remote add origin ${GIT_PROJECT_URL}
	git fetch origin
	git checkout -f ${GIT_WORKING_BRANCH}

build: ## Build container
	bash ./scripts/docker-compose.sh build-$(target)

up: ## Run container in dl1
	bash ./scripts/docker-compose.sh up-$(target) faceembedder

down: ## Stop and remove a running container
	bash ./scripts/docker-compose.sh down-$(target)

exec: ## Run a bash in a running container
	$(eval CONTAINER_NAME=$(call env_arg,CONTAINER_NAME))
	nvidia-docker exec -it ${CONTAINER_NAME}-$(target) bash

compile-requirements: ## compile dev and prod requirements.txt
	pip-compile ./requirements/prod-requirements.in
	pip-compile ./requirements/dev-requirements.in

port-forwarding-to: ## Up and down a direct tunnel to the docker container
	$(eval NAME=$(call env_arg,$(server)PW_NAME))
	$(eval LOCAL_ADDR=$(call env_arg,$(server)PW_LOCAL_ADDR))
	$(eval LOCAL_PORT=$(call env_arg,$(server)PW_LOCAL_PORT))
	$(eval REMOTE_ADDR=$(call env_arg,$(server)PW_REMOTE_ADDR))
	$(eval HOST_SSH_PORT=$(call env_arg,HOST_SSH_PORT))
	$(eval REMOTE_SSH=$(call env_arg,$(server)PW_REMOTE_SSH))
	$(eval SSH_USER=$(call env_arg,$(server)PW_SSH_USER))

	bash ./scripts/port_forwarding.sh \
	 	--name=${NAME} \
	 	--local-addr=${LOCAL_ADDR} \
	 	--local-port=${LOCAL_PORT} \
	 	--remote-addr=${REMOTE_ADDR} \
	 	--remote-port=${HOST_SSH_PORT} \
	 	--remote-ssh=${REMOTE_SSH} \
	 	--ssh-user=${SSH_USER} \
	 	--command=$(command)

assign-datadir: ## Assign face_datasets directory to data directory as symlink
	rm ./data
	$(eval DATASETS_DIRPATH=$(call env_arg,$(server)_DATASETS_DIRPATH))
	ln -s ${DATASETS_DIRPATH} ./data
