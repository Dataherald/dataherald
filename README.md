# dataherald

<p align="center">
  <a href="https://dataherald.com"><img src="https://files.dataherald.com/logos/dataherald.png" alt="Dataherald logo"></a>
</p>

<p align="center">
    <b>Dataherald - query your structured data in natural language</b>. <br />
</p>

<p align="center">
  <a href="https://discord.gg/A59Uxyy2k9" target="_blank">
      <img src="https://img.shields.io/discord/1138593282184716441" alt="Discord">
  </a> |
  <a href="https://www.dataherald.com/" target="_blank">
      <img src="https://img.shields.io/static/v1?label=license&message=Apache 2.0&color=white" alt="License">
  </a> |
  <a href="https://www.dataherald.com/" target="_blank">
      Docs
  </a> |
  <a href="https://www.dataherald.com/" target="_blank">
      Homepage
  </a>
</p>

Dataherald is a text-to-sql engine built for enteprise-level question answering over structured data. It allows you to set up an API from your database that can answer questions in plain English. You can use Dataherald to:

- Allow business users to get insights from the data warehouse without going through a data analyst
- Enable Q+A from your production DBs inside your SaaS application
- Create a ChatGPT plug-in from your proprietary data

... and many more!

This project is undergoing swift development, and as such, the API may be subject to change at any time.

## Overview

### Background

The latest LLMs have gotten remarkably good at writing SQL. However we could not get existing frameworks to work with our structured data at a level which we could incorporate into our application. That is why we built and released this engine.

### Goals

Dataherald is built to:

- Be modular, allowing different implementations of core components to be plugged-in
- Come batteries included: Have best-in-class implementations for components like text to SQL, evaluation   
- Be easy to set-up and use with major data waarehouses
- Get better with usage
- Be fast

## Get Started

The simplest way to set up Dataherald is to use to use the hosted version. We are rolling this service to select customers. Sign up for the <a href="https://www.dataherald.com/contact" target="_blank">waitlist</a>.

You can also self-host the engine locally using Docker. By default the engine uses Mongo to store application data.

## How to Run Dataherald (with local Mongo) with Docker

1. Create `.env` file, you can use the `.env.example` file as a guide
```
cp .env.example .env
```

2. Install and run Docker

3. Create a Docker network for communication between services. 
>We need to set it up externally to enable external clients running on docker to communicate with this app. 
Run the following command:
```
docker network create backendnetwork
```

4. Build docker images, create containers and raise them. This will raise the app and mongo container
```
docker-compose up --build
```
> You can skip the `--build` if you don't have to rebuild the image due to updates to the dependencies

5. Check that the containers are running, you should see 2 containers
```
docker ps
```
It should look like this:
```
CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS         PORTS                      NAMES
72aa8df0d589   dataherald-app   "uvicorn dataherald.…"   7 seconds ago   Up 6 seconds   0.0.0.0:80->80/tcp         dataherald-app-1
6595d145b0d7   mongo:latest     "docker-entrypoint.s…"   19 hours ago    Up 6 seconds   0.0.0.0:27017->27017/tcp   dataherald-mongodb-1
```

6. In your browser visit [http://localhost/docs](http://localhost/docs)



## See Docker App container logs
Once app container is running just execute the next command
```
docker-compose exec app cat dataherald.log
```

## Connect to Docker MongoDB container
Once your mongo container is running you can use any tool (Such as NoSQLBooster) to connect it.
The default values are:
```
HOST: localhost # inside the docker containers use the host "mongodb" and outside use "localhost"
PORT: 27017
DB_NAME: dataherald
DB_USERNAME = admin
DB_PASSWORD = admin
```

## DB Connections
DB credentials are stored in `database_connection` collection in MongoDB and we can use the endpoint `/api/v1/database`
to set the credentials. Beside when the application starts it stores a default db connection which takes the fields from
the .env file.

So to generate the default db connection when the app starts is important to set this env vars.
Using ssh
```
SSH_ENABLED = True
SSH_HOST = 'dev-box.dataherald.com'
SSH_USERNAME='<your-user>'
SSH_PASSWORD='<your-pass>'
SSH_REMOTE_HOST = 'higeorge-production.cocfmuuqq1ym.us-east-1.rds.amazonaws.com'
SSH_PRIVATE_KEY_PATH = '/app/id_rsa'
SSH_PRIVATE_KEY_PASSWORD = '<your-pass>'
SSH_REMOTE_DB_NAME = 'postgres'
SSH_REMOTE_DB_PASSWORD = '<your-pass>'
SSH_DB_DRIVER = 'postgresql+psycopg2'
DATABASE_URI = ''
```

Without ssh
```
SSH_ENABLED = False
DATABASE_URI = '<db-connection-uri>'
```

## Data encryption

To encrypt and decrypt sensitive Database connection data that is stored in Mongo an encryption key is required. This can be set in the `ENCRYPT_KEY`field of the .env file

### Generate a new key
```
# Install the package cryptography in the terminal
pip3 install cryptography

# Run python in terminal
python3

# Import Fernet
from cryptography.fernet import Fernet

# Generate the key
Fernet.generate_key()
```


## Contributing
As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see [here](CONTRIBUTING.md).


### DB errors

Try completely deleting `/dbdata` before rebuilding the databases to ensure there is no corrupted data.