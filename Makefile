# There must be no space between the function name and the input argument
# Example: $(call env_arg,NAME))
#                        ^
define env_arg
	$(shell grep -oP '^$(1)=\K.*' .env)
endef


help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build container
	bash ./scripts/docker-compose.sh build-$(target)

up: ## Run container
	bash ./scripts/docker-compose.sh up-$(target) $(server) faceembedder

down: ## Stop and remove a running container
	bash ./scripts/docker-compose.sh down-$(target) $(server)

exec: ## Run a bash in a running container
	$(eval CONTAINER_NAME=$(call env_arg,CONTAINER_NAME))
	nvidia-docker exec -it ${CONTAINER_NAME}-$(target) bash

compile-requirements: ## Compile dev and prod requirements.txt
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

git-server-init: ## Initializing the repository to use the git metadata in the docker
	$(eval GIT_PROJECT_URL=$(call env_arg,GIT_PROJECT_URL))
	$(eval GIT_WORKING_BRANCH=$(call env_arg,GIT_WORKING_BRANCH))

	git init
	git remote add origin ${GIT_PROJECT_URL}
	git fetch origin
	git checkout -f ${GIT_WORKING_BRANCH}
