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
  <a href="./LICENSE" target="_blank">
      <img src="https://img.shields.io/static/v1?label=license&message=Apache 2.0&color=white" alt="License">
  </a> |
  <a href="https://dataherald.readthedocs.io/" target="_blank">
      Docs
  </a> |
  <a href="https://www.dataherald.com/" target="_blank">
      Homepage
  </a>
</p>


Dataherald is a natural language-to-SQL engine built for enterprise-level question answering over structured data. It allows you to set up an API from your database that can answer questions in plain English. You can use Dataherald to:

- Allow business users to get insights from the data warehouse without going through a data analyst
- Enable Q+A from your production DBs inside your SaaS application
- Create a ChatGPT plug-in from your proprietary data


This project is undergoing swift development, and as such, the API may be subject to change at any time.

If you would like to learn more, you can join the <a href="https://discord.gg/A59Uxyy2k9" target="_blank">Discord</a> or <a href="https://dataherald.readthedocs.io/" target="_blank">read the docs</a>.

## Overview

### Background

The latest LLMs have gotten remarkably good at writing syntactically correct SQL. However since they lack business context, they often write inaccurate SQL. Our goal with Dataherald is to build the more performant and easy to use NL-to-SQL product for developers.

### Goals

Dataherald is built to:

- Have the highest accuracy and lowest latency possible
- Be easy to set-up and use with major data warehouses
- Enable users to add business context from various sources
- Give developers the tools to fine-tune NL-to-SQL models on their own schema and deploy them in production
- Be LLM provider agnostic

## Get Started

The simplest way to set up Dataherald is to use the hosted version. We are rolling this service to select customers. Sign up for the <a href="https://www.dataherald.com/contact" target="_blank">waitlist</a>.

You can also self-host the engine locally using Docker. By default the engine uses Mongo to store application data.


## How to Run Dataherald (with local Mongo) using Docker

1. Create `.env` file, you can use the `.env.example` file as a guide. You must set these fields for the engine to start. 

```
cp .env.example .env
```

Specifically the following fields must be manually set before the engine is started.

```
#OpenAI credentials and model 
# mainly used for embedding models and finetunung 
OPENAI_API_KEY = 
ORG_ID =

#Encryption key for storing DB connection data in Mongo
ENCRYPT_KEY = 

# the variable that determines how many rows should be returned from a query to the agents, set it to small values to avoid high costs and long response times, default is 50
UPPER_LIMIT_QUERY_RETURN_ROWS = 50
# the variable that force the engine to quit if the sql geneation takes more than the time set in this variable, default is None.
DH_ENGINE_TIMEOUT = 150
```

In case you want to use models deployed in Azure OpenAI, you must set the following variables:
```
AZURE_API_KEY = "xxxxx"
AZURE_OPENAI_API_KEY = "xxxxxx"
API_BASE = "azure_openai_endpoint" 
AZURE_OPENAI_ENDPOINT = "azure_openai_endpoint" 
AZURE_API_VERSION = "version of the API to use"
LLM_MODEL = "name_of_the_deployment"
EMBEDDING_MODEL = "name_of_deployed_embedding_model"
```
In addition, an embedding model will be also used. There must be a deployment created with name "text-embedding-3-large".

The existence of AZURE_API_KEY as environment variable indicates Azure models must be used. 

Remember to remove comments beside the environment variables.

While not strictly required, we also strongly suggest you change the MONGO username and password fields as well.

Follow the next commands to generate an ENCRYPT_KEY and paste it in the .env file like 
this `ENCRYPT_KEY = 4Mbe2GYx0Hk94o_f-irVHk1fKkCGAt1R7LLw5wHVghI=`

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

2. Install and run Docker

3. Create a Docker network for communication between services. 
>We need to set it up externally to enable external clients running on docker to communicate with this app. 
Run the following command:
```
docker network create dataherald_network
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
6595d145b0d7   mongo:latest     "docker-entrypoint.s…"   19 hours ago    Up 6 seconds   0.0.0.0:27017->27017/tcp   mongodb
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

## Connecting to and Querying your SQL Databases
Once the engine is running, you will want to use it by:
1. Connecting to you data warehouses
2. Adding context about the data to the engine
3. Querying the data in natural language

### Connecting to your data warehouses
We currently support connections to Postgres, DuckDB, BigQuery, ClickHouse, Databricks, Snowflake, MySQL/MariaDB, MS SQL Server, Redshift and AWS Athena. You can create connections to these warehouses through the API or at application start-up using the envars.

#### Connecting through the API

You can define a DB connection through a call to the following API endpoint `POST /api/v1/database-connections`. For example:

```
curl -X 'POST' \
  '<host>/api/v1/database-connections' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "alias": "my_db_alias",
  "use_ssh": false,
  "connection_uri": snowflake://<user>:<password>@<organization>-<account-name>/<database>/<schema>"
}'
```

##### Connecting multi-schemas
You can connect many schemas using one db connection if you want to create SQL joins between schemas.
Currently only `BigQuery`, `Snowflake`, `Databricks` and `Postgres` support this feature.
To use multi-schemas instead of sending the `schema` in the `connection_uri` set it in the `schemas` param, like this:

```
curl -X 'POST' \
  '<host>/api/v1/database-connections' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "alias": "my_db_alias",
  "use_ssh": false,
  "connection_uri": snowflake://<user>:<password>@<organization>-<account-name>/<database>",
  "schemas": ["schema_1", "schema_2", ...]
}'
```

##### Connecting to supported Data warehouses and using SSH
You can find the details on how to connect to the supported data warehouses in the [docs](https://dataherald.readthedocs.io/en/latest/api.create_database_connection.html)

### Adding Context
Once you have connected to the data warehouse, you can add context to the engine to help improve the accuracy of the generated SQL. Context can currently be added in one of three ways:

1. Scanning the Database tables and columns
2. Adding verified SQL (golden SQL)
3. Adding string descriptions of the tables and columns
4. Adding database level instructions

While only the Database scan part is required to start generating SQL, adding verified SQL and string descriptions are also important for the tool to generate accurate SQL. 

#### Scanning the Database
The database scan is used to gather information about the database including table and column names and identifying low cardinality columns and their values to be stored in the context store and used in the prompts to the LLM.
In addition, it retrieves logs, which consist of historical queries associated with each database table. These records are then stored within the query_history collection. The historical queries retrieved encompass data from the past three months and are grouped based on query and user.
The db_connection_id param is the id of the database connection you want to scan, which is returned when you create a database connection.
The ids param is the table_description_id that you want to scan.
You can trigger a scan of a database from the `POST /api/v1/table-descriptions/sync-schemas` endpoint. Example below


```
curl -X 'POST' \
  '<host>/api/v1/table-descriptions/sync-schemas' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "db_connection_id": "db_connection_id",
    "ids": ["<table_description_id_1>", "<table_description_id_2>", ...]
  }'
```

Since the endpoint identifies low cardinality columns (and their values) it can take time to complete. 

#### Get logs per db connection
Once a database was scanned you can use this endpoint to retrieve the tables logs
Set the `db_connection_id` to the id of the database connection you want to retrieve the logs from

```
curl -X 'GET' \
  'http://localhost/api/v1/query-history?db_connection_id=656e52cb4d1fda50cae7b939' \
  -H 'accept: application/json'
```

Response example:
```
[
  {
    "id": "656e52cb4d1fda50cae7b939",
    "db_connection_id": "656e52cb4d1fda50cae7b939",
    "table_name": "table_name",
    "query": "select QUERY_TEXT, USER_NAME, count(*) as occurrences from ....",
    "user": "user_name",
    "occurrences": 1
  }
]
```

#### Adding verified SQL

Adding ground truth Question/SQL pairs is a powerful way to improve the accuracy of the generated SQL. Golden records can be used either to fine-tune the LLM or to augment the prompts to the LLM.

You can read more about this in the [docs](https://dataherald.readthedocs.io/en/latest/api.golden_sql.html)

#### Adding string descriptions
In addition to database table_info and golden_sql, you can set descriptions or update the columns per table and column. 
Description are used by the agents to determine the relevant columns and tables to the user's question.

Read more about this in the [docs](https://dataherald.readthedocs.io/en/latest/api.update_table_descriptions.html)

#### Adding database level instructions

Database level instructions are passed directly to the engine and can be used to steer the engine to generate SQL that is more in line with your business logic. This can include instructions such as "never use this column in a where clause" or "always use this column in a where clause".

You can read more about this in the [docs](https://dataherald.readthedocs.io/en/latest/api.add_instructions.html)


### Querying the Database in Natural Language
Once you have connected the engine to your data warehouse (and preferably added some context to the store), you can query your data warehouse using the `POST /api/v1/prompts/sql-generations` endpoint.

```
curl -X 'POST' \
  '<host>/api/v1/prompts/sql-generations' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
        "finetuning_id": "string", # specify the finetuning id if you want to use a finetuned model
        "low_latency_mode": false, # low latency mode is used to generate SQL faster, but with lower accuracy
        "llm_config": {
          "llm_name": "gpt-4-turbo-preview", # specify the LLM model you want to use
          "api_base": "string" # If you are using open-source LLMs, you can specify the API base. If you are using OpenAI, you can leave this field empty
        },
        "evaluate": false, # if you want our engine to evaluate the generated SQL
        "sql": "string", # if you want to evaluate a specific SQL pass it here, else remove this field to generate SQL from a question
        "metadata": {},
        "prompt": {
          "text": "string", # the question you want to ask
          "db_connection_id": "string", # the id of the database connection you want to query
          "metadata": {}
        }
    }'
```

### Create a natural language response and SQL generation for a question
If you want to create a natural language response and a SQL generation for a question, you can use the `POST /api/v1/prompts/sql-generations/nl-generations` endpoint.

```
curl -X 'POST' \
  '<host>/api/v1/responses?run_evaluator=true&sql_response_only=false&generate_csv=false' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
        "llm_config": {
          "llm_name": "gpt-4-turbo-preview", # specify the LLM model you want to use to generate the NL response
          "api_base": "string" # If you are using open-source LLMs, you can specify the API base. If you are using OpenAI, you can leave this field empty
        },
        "max_rows": 100, # the maximum number of rows you want to use for generating the NL response
        "metadata": {},
        "sql_generation": {
          "finetuning_id": "string", # specify the finetuning id if you want to use a finetuned model
          "low_latency_mode": false, # low latency mode is used to generate SQL faster, but with lower accuracy
          "llm_config": {
            "llm_name": "gpt-4-turbo-preview", # specify the LLM model you want to use to generate the SQL
            "api_base": "string" # If you are using open-source LLMs, you can specify the API base. If you are using OpenAI, you can leave this field empty
          },
          "evaluate": false, # if you want our engine to evaluate the generated SQL
          "sql": "string",  # if you want to evaluate a specific SQL pass it here, else remove this field to generate SQL from a question
          "metadata": {}
          "prompt": {
            "text": "string", # the question you want to ask
            "db_connection_id": "string", # the id of the database connection you want to query
            "metadata": {}
          }
        },
}'
```

### How to migrate data between versions
Our engine is under ongoing development and in order to support the latest features, we provide scripts to migrate the data from the previous version to the latest version. You can find all of the scripts in the `dataherald.scripts` module. To run the migration script, execute the following command:

```
docker-compose exec app python3 -m dataherald.scripts.migrate_v100_to_v101
```

## Replacing core modules
The Dataherald engine is made up of replaceable modules. Each of these can be replaced with a different implementation that extends the base class. Some of the main modules are:

1. SQL Generator -- The module that generates SQL from a given natural language question. 
2. Vector Store -- The Vector DB used to store context data such as sample SQL queries
3. DB -- The DB that persists application logic. By default this is Mongo.
4. Evaluator -- A module which evaluates accuracy of the generated SQL and assigns a score. 

In some instances we have already included multiple implementations for testing and benchmarking. 

## Contributing
As an open-source project in a rapidly developing field, we are open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see [here](CONTRIBUTING.md).
