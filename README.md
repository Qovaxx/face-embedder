# face-embedder

* Deploy Token:
    * CI_DEPLOY_USER: `gitlab+deploy-token-43`
    * CI_DEPLOY_PASSWORD: `KXUyt17jsfNfTdm1qbv7`
    * TOKEN: `git clone http://gitlab+deploy-token-43:KXUyt17jsfNfTdm1qbv7@gitlab.x5.ru/computer-vision/face-embedder.git`
    
* Commands:
    * Run docker container:
        ```bash
        make build target=[dev|prod]
        make up target=[dev|prod]
        make exec target=[dev|prod]
        ```
    
    * Stop and rm container:
        ```bash
        make down target=[dev|prod]
        ```
        
    * Port-forwarding to the server with running container:
        ```bash
        make dl1-port-forwarding command=[start|stop]
        ```
    
    * Compile dev and prod requirements `./requirements/`:
        ```bash
        make compile-requirements
        ```