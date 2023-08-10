# K2 Server

This is a fastapi application that handles the business logic k2 enterprise and exposes k2-core API externally

## Building and Running with Docker
We use Docker to create a reproducible environment for k2-server.

1. Create your local `.env` file and copy the variables from `.env.example` and fill them up

2. Create a Docker network for communication between services. 
>We need to set it up externally to enable external clients running on docker to communicate with this app. 
Run the following command:
```
docker network create backendnetwork
```
>If you are running k2-core locally on docker, you can find container's IP by running this command:
```
docker inspect <container_id> | grep IPAddress
```

3. Build the Docker container
```
docker-compose build
```

4. Run the Docker container:
```
docker-compose up
```