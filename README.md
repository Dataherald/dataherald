# dataherald

<p align="center">
  <a href="https://dataherald.com"><img src="https://files.dataherald.com/logos/dataherald.png" alt="Dataherald logo"></a>
</p>

<p align="center">
    <b>Query your structured data in natural language</b>. <br />
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

1. Create `.env` file, you can use the `.env.example` file as a guide. You must set these fields for the engine to start. 
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



### See Docker App container logs
Once app container is running just execute the next command
```
docker-compose exec app cat dataherald.log
```

### Connect to Docker MongoDB container
Once your mongo container is running you can use any tool (Such as NoSQLBooster) to connect it.
The default values are:
```
HOST: localhost # inside the docker containers use the host "mongodb" and outside use "localhost"
PORT: 27017
DB_NAME: dataherald
DB_USERNAME = admin
DB_PASSWORD = admin
```

## Connecting to and Querying data stores
Once the engine is running, you will want to use it by:
1- Connecting to you data warehouses
2- Adding context about the data to the engine
3- Querying the data in natural language

### Connecting to your data warehouses
We currently support connections to PostGres, BigQuery, Databricks and Snowflake. You can create connections to these warehouses through the API or at application start-up using the envars.

#### Connecting through the API

You can define a DB connection through a call to the following API endpoint `/api/v1/database`. For example

```


```

By default, DB credentials are stored in `database_connection` collection in MongoDB. Connection URI information is encrypted using the key you provide as an environment variable (see below)

#### Encrypting sensitive DB credentials

To encrypt and decrypt sensitive Database connection data that is stored in Mongo an encryption key is required. This can be set in the `ENCRYPT_KEY`field of the .env file

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

#### Connecting through envars
Alternatively, you can store a default db connection to be read in when the application starts from the .env file. We only recommend this if you need to access your Database through an SSH tunnel. 

So to generate the default db connection when the app starts is important to set this env vars.
Using ssh
```
SSH_ENABLED = True
SSH_HOST = '<ssh-host domain name>'
SSH_USERNAME='<your-user>'
SSH_PASSWORD='<your-pass>'
SSH_REMOTE_HOST = '<remote host name>'
SSH_PRIVATE_KEY_PATH = '/app/id_rsa'
SSH_PRIVATE_KEY_PASSWORD = '<your-pass>'
SSH_REMOTE_DB_NAME = '<remote db name>'
SSH_REMOTE_DB_PASSWORD = '<your-pass>'
SSH_DB_DRIVER = 'postgresql+psycopg2'
DATABASE_URI = ''
```

Without ssh
```
SSH_ENABLED = False
DATABASE_URI = '<db-connection-uri>'
```


### Adding Context
Once you have connected to the data warehouse, you should add context to the engine to help improve the accuracy of the generated SQL. While this step is optional, it is necessary for the tool to generate accurate SQL. Context can currently be added in one of three ways:

1- Scanning the Database tables and columns
2- Adding verified SQL (golden SQL)
3- Adding string descriptions of the tables and columns

#### Scanning the Database
The database scan is used to gather information about the database including table and column names and identifying low cardinality columns and their values to be stored in the context store and used in the prompts to the LLM. You can trigger a scan of a database from the following endpoint

```

```

#### Adding verified SQL
Sample NL<>SQL pairs (golden SQL) can be stored in the context store and used for few-shot in context learning. In the default context store and NL 2 SQL engine, these samples are stored in a vector store and the closest samples are retrieved for few shot learning. You can add golden SQL to the context store from the following API endpoint

```

```

#### Adding string descriptions
In addition to database table_info and golden_sql, you can add strings describing tables and/or columns to the context store manually from the following API endpoint


### Querying the Database in Naturual Language
Once you have connected the engine to your data warehouse (and preferably added some context to the store), you can query your data warehouse using the following endpoint.

```

```


## Replacing core modules
The Dataherald engine is made up 

## Contributing
As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see [here](CONTRIBUTING.md).


### Mongo errors

The Mongo installation is configured to store application data in the `/dbdata` folder. In case you want to wipe the local DB, try completely deleting `/dbdata` before rebuilding the databases.