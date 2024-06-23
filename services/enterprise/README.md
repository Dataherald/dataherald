# Enterprise Server

The "Enterprise Server" (or ai-server) is a fastapi backend application that implements the business logic that is exposed to the users in the front-end clients like Admin Console and Slackbot. This includes authentication and authorization (both API keys and UI). The application is built on top of the dataherald engine and the two access the same MongoDB instance for storage. Before running this application you need to be running the Dataherald engine.

## Building and Running with Docker Locally
We use Docker to create the environment ai-server.
> Please use the dockerfile instead of the docker-compose file if you are trying to deploy it on your cloud platform.

1. Create your local `.env` file and copy the variables from `.env.example` and fill them up

2. Create a Docker network for communication between services. 
>We need to set it up externally to enable external clients running on docker to communicate with this app. 
Run the following command:
```
docker network create dataherald_network
```
>If you are running ai-engine locally on docker, you can find container's IP by running this command:
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

## Setting up Authentication with Auth0
To connect to Auth0 you will need to fill in the following environment variables before running the app:
```
AUTH0_DOMAIN=
AUTH0_ISSUER_BASE_URL=
AUTH0_API_AUDIENCE=
AUTH0_DISABLED=False
```

Please, read the front-end docs about Auth0 [here](../admin-console/README.md#setting-up-an-auth0-application) if you have troubles setting this up.

## Setting up Stripe 
To get the stripe api key for local development, go to stripe's developer dashboard in test mode (https://dashboard.stripe.com/test/developers), then go to the API keys tab and either use the exising key named `test key` or create a new one with the appropriate permissions.

To get the stripe webhook secret go to the Webhook tab instead and click `Add local listener`.


>If you would like to disable stripe, make sure to change your organization's plan to `ENTERPRISE`.

## Testing (deprecated)

### API Tests
To run the Postman API test locally, use the Postman CLI:
```
postman login --with-api-key
postman collection run "tests/postman/ai-api-test.json
```
Can you also use the Postman UI to run the tests instead, the test suite is under project `DHAI` from APIs in Postman.

Besure to choose the appropriate enviornment from postman. For local environment, run the initialzation script first.

### Unit Tests
To test the endpoints in the server, create your python enviornment with required packages installed and run the pytest:
```
python3 -m pytest tests/
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

## Run Enterprise and Engine containers
Follow these steps to set up and run the Enterprise and Engine containers for local development:

1. Create the docker network if it doesn't exist
```
docker network create dataherald_network
```

2. Set the envvars in the .env file for `server` and `dataherald` projects
```
cp .env.example .env
```

3. Make sure you use the same `ENCRYPT_KEY` for `server` and `dataherald`.


4. For `ENGINE_URL` check that you use as host the service name that is specified in docker-composer file, for example:
```
ENGINE_URL=http://app/api/v1
```

5. Run the containers and execute the initialization script to generate data. It should create a real db_connection, 
an organization and a valid api-key.
```
make start
```
