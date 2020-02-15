# face-embedder

## Commands:
* Run docker container:
    ```bash
    make build target=[dev|prod]
    make up target=[dev|prod] server=[DL1|DL2|DL4]
    make exec target=[dev|prod]
    ```

* Stop and rm container:
    ```bash
    make down target=[dev|prod] server=[DL1|DL2|DL4]
    ```
    
* Port-forwarding to the server with running container:
    ```bash
    make port-forwarding-to server=[DL1|DL2|DL4] command=[start|stop]
    ```

* Compile dev and prod requirements `./requirements/`:
    ```bash
    make compile-requirements
    ```

## Project setup example:
Correct the variables and paths in the .env file first
```
[dl1]: make compile-requirements
[dl1]: make git-server-init
[dl1]: make build target=dev
[dl1]: make up target=dev server=DL1
[notebook]: make port-forwarding-to server=DL1 command=start
```
