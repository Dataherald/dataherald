# K2 Enterprise

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

## Testing
To test the endpoints in the server, create your python enviornment with required packages installed and run the pytest:
```
python3 -m pytest test/
```

The test does not cover end to end testing and mocks authentication, authorization, and repository objects. 

## Migration
To run a migration script use the following command:
```
docker-compose exec app python3 -m database.migrations.sprint_xx.script_name
```

## Run reporting script
1. Register the public IP in https://cloud.mongodb.com/, click "Network access" and click "ADD IP ADDRESS".
2. Set your envvars in the .env file, for example:
```
MONGODB_DB_NAME=dataherald
MONGODB_URI=mongodb://admoulin:admin@mongodb:27017 # update mongo URI
```
3. Build the container to take the envvars changes, check that you are located in this path `monorepo/apps/ai/server`
```
docker-compose up --build
```
4. To run a migration script use the following commands:
Check the docker container id
```
docker ps
```

Run the script specifying the container_id and `organization_id`, `question_date_gte` and `question_date_gte` parameters are optional
```
docker exec <container_id> python3 -m database.scripts.data_report organization_id 64f772407fc2d1535ccdcfab question_date_gte 2024-11-01 question_date_lt 2024-11-24
```

5. It should create a csv file if there is data