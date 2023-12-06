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

The latest LLMs have gotten remarkably good at writing SQL. However we could not get existing frameworks to work with our structured data at a level which we could incorporate into our application. That is why we built and released this engine.

### Goals

Dataherald is built to:

- Be modular, allowing different implementations of core components to be plugged-in
- Come batteries included: Have best-in-class implementations for components like text to SQL, evaluation   
- Be easy to set-up and use with major data warehouses
- Get better with usage
- Be fast

## Get Started

The simplest way to set up Dataherald is to use the hosted version. We are rolling this service to select customers. Sign up for the <a href="https://www.dataherald.com/contact" target="_blank">waitlist</a>.

You can also self-host the engine locally using Docker. By default the engine uses Mongo to store application data.


## How to Run Dataherald (with local Mongo) using Docker

1. Create `.env` file, you can use the `.env.example` file as a guide. You must set these fields for the engine to start. 

```
cp .env.example .env
```

Specifically the following 5 fields must be manually set before the engine is started.

LLM_MODEL is employed by the engine to generate SQL from natural language. You can use the default model (gpt-4-1106-preview) or use your own.

```
#OpenAI credentials and model 
OPENAI_API_KEY = 
LLM_MODEL = 
ORG_ID =

#Encryption key for storing DB connection data in Mongo
ENCRYPT_KEY = 

# All of our SQL generation agents are using different tools to generate SQL queries, in order to limit the number of times that agents can
# use different tools you can set the "AGENT_MAX_ITERATIONS" env variable. By default it is set to 20 iterations.

```

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

## Connecting to and Querying your SQL Databases
Once the engine is running, you will want to use it by:
1. Connecting to you data warehouses
2. Adding context about the data to the engine
3. Querying the data in natural language

### Connecting to your data warehouses
We currently support connections to Postgres, BigQuery, Databricks, Snowflake and AWS Athena. You can create connections to these warehouses through the API or at application start-up using the envars.

#### Connecting through the API

You can define a DB connection through a call to the following API endpoint `POST /api/v1/database-connections`. For example:

Example 1. Without a SSH connection
```
curl -X 'POST' \
  '<host>/api/v1/database-connections' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "alias": "my_db_alias",
  "use_ssh": false,
  "connection_uri": "sqlite:///mydb.db",
  "path_to_credentials_file": "my-folder/my-secret.json" # Required for bigquery
}'
```

Example 2. With a SSH connection
```
curl -X 'POST' \
  '<host>/api/v1/database-connections' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "alias": "my_db_alias",
  "use_ssh": true,
  "ssh_settings": {
    "db_name": "db_name",
    "host": "string",
    "username": "string",
    "password": "string",
    "remote_host": "string",
    "remote_db_name": "string",
    "remote_db_password": "string",
    "private_key_password": "string",
    "db_driver": "string"
  }
}'
```
If you need to set up an SSH connection to connect to your DB you need to fill out all the ssh_settings fields

By default, DB credentials are stored in `database_connection` collection in MongoDB. Connection URI information is encrypted using the ENCRYPT_KEY you provided as an environment variable

##### Connecting to supported Data warehouses
You can generate the `connection_uri` parameter in the API call for each of the supported warehouses by using the steps outlined below.

**Postgres**
```
"connection_uri": postgresql+psycopg2://<user>:<password>@<host>:<port>/<db-name>
```

**Databricks**
```
"connection_uri": databricks://token:<token>@<host>?http_path=<http-path>&catalog=<catalog>&schema=<schema-name>
```

**Snowflake**
```
"connection_uri": snowflake://<user>:<password>@<organization>-<account-name>/<database>/<schema>
```

**AWS Athena**
```
"connection_uri": awsathena+rest://<aws_access_key_id>:<aws_secret_access_key>@athena.<region_name>.amazonaws.com:443/<schema_name>?s3_staging_dir=<s3_staging_dir>&work_group=primary
```

**DuckDB**
To connect to DuckDB you should first host your database in MotherDuck and fetch your authentication token.
```
"connection_uri": duckdb:///md:<database_name>?motherduck_token=<your_token>
```

**BigQuery**
To connect to BigQuery you should create a json credential file. Please follow Steps 1-3 under "Configure 
BigQuery Authentication in Google Cloud Platform" in 
this [tutorial](https://www.privacydynamics.io/docs/connections/bigquery.html). 

> IMPORTANT: Please ensure the service account only has **"Viewer"** permissions.

Once you have your credential json file you can store it inside this project for example I created the folder 
`private_credentials` and inside I stored my credential file `my-db-123456acbd.json`

You should set in the endpoint param `path_to_credentials_file` the path, for example:
```
"path_to_credentials_file": "private_credentials/my-db-123456acbd.json"
```

```
"connection_uri": bigquery://<project>/<database>
```



### Adding Context
Once you have connected to the data warehouse, you should add context to the engine to help improve the accuracy of the generated SQL. Context can currently be added in one of three ways:

1. Scanning the Database tables and columns
2. Adding verified SQL (golden SQL)
3. Adding string descriptions of the tables and columns

While only the Database scan part is required to start generating SQL, adding verified SQL and string descriptions are also important for the tool to generate accurate SQL. 

#### Scanning the Database
The database scan is used to gather information about the database including table and column names and identifying low cardinality columns and their values to be stored in the context store and used in the prompts to the LLM.
In addition, it retrieves logs, which consist of historical queries associated with each database table. These records are then stored within the query_history collection. The historical queries retrieved encompass data from the past three months and are grouped based on query and user.
You can trigger a scan of a database from the `POST /api/v1/table-descriptions/sync-schemas` endpoint. Example below


```
curl -X 'POST' \
  '<host>/api/v1/table-descriptions/sync-schemas' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "db_connection_id": "db_connection_id",
    "table_names": ["table_name"]
  }'
```

Since the endpoint identifies low cardinality columns (and their values) it can take time to complete. Therefore while it is possible to trigger a scan on the entire DB by not specifying the `table_names`, we recommend against it for large databases. 

#### Get logs per db connection
Once a database was scanned you can use this endpoint to retrieve the tables logs

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

#### Get a scanned db
Once a database was scanned you can use this endpoint to retrieve the tables names and columns


```
curl -X 'GET' \
  '<host>/api/v1/table-descriptions?db_connection_id=64dfa0e103f5134086f7090c&table_name=foo' \
  -H 'accept: application/json'
```

#### Adding verified SQL
Sample NL<>SQL pairs (golden SQL) can be stored in the context store and used for few-shot in context learning. In the default context store and NL 2 SQL engine, these samples are stored in a vector store and the closest samples are retrieved for few shot learning. You can add golden SQL to the context store from the `POST /api/v1/golden-records` endpoint

```
curl -X 'POST' \
  '<host>/api/v1/golden-records' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
        {
            "nl_question":"what was the most expensive zip code to rent in Los Angeles county in May 2022?", 
            "sql": "SELECT location_name, metric_value FROM table_name WHERE dh_county_name = '\''Los Angeles'\'' AND dh_state_name = '\''California'\''   AND period_start='\''2022-05-01'\'' AND geo_type='\''zip'\'' ORDER BY metric_value DESC LIMIT 1;", 
            "db":"db_name"
        }
  ]'
```

#### Adding string descriptions
In addition to database table_info and golden_sql, you can set descriptions or update the columns per table and column. 
All request body fields are optional, and only the fields that are explicitly set will be used to update the resource.

```
curl -X 'PATCH' \
  '<host>/api/v1/table-descriptions/64dfa0e103f5134086f7090c' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "description": "Table description",
  "columns": [
    {
      "name": "column1",
      "description": "string",
      "is_primary_key": false,
      "data_type": "string",
      "low_cardinality": true,
      "categories": [
        "string"
      ],
      "foreign_key": false
    },
    {
      "name": "column2",
      "description": "string",
      "is_primary_key": false,
      "data_type": "string",
      "low_cardinality": true,
      "categories": [
        "string"
      ],
      "foreign_key": false
    }
  ]
}'
```

#### Adding database level instructions

You can add database level instructions to the context store manually from the `POST /api/v1/instructions` endpoint.
These instructions are passed directly to the engine and can be used to steer the engine to generate SQL that is more in line with your business logic.

```
curl -X 'POST' \
  '<host>/api/v1/instructions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "instruction": "This is a database level instruction"
  "db_connection_id": "db_connection_id"
}'
```

#### Getting database level instructions

You can get database level instructions from the `GET /api/v1/instructions` endpoint

```
curl -X 'GET' \
  '<host>/api/v1/instructions?page=1&limit=10&db_connection_id=12312312' \
  -H 'accept: application/json'
```

#### Deleting database level instructions

You can delete database level instructions from the `DELETE /api/v1/instructions/{instruction_id}` endpoint

```
curl -X 'DELETE' \
  '<host>/api/v1/instructions/{instruction_id}' \
  -H 'accept: application/json'
```

#### Updating database level instructions

You can update database level instructions from the `PUT /api/v1/instructions/{instruction_id}` endpoint
Try different instructions to see how the engine generates SQL

```
curl -X 'PUT' \
  '<host>/api/v1/instructions/{instruction_id}' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "instruction": "This is a database level instruction"
}'
```


### Querying the Database in Natural Language
Once you have connected the engine to your data warehouse (and preferably added some context to the store), you can query your data warehouse using the `POST /api/v1/questions` endpoint.

```
curl -X 'POST' \
  '<host>/api/v1/questions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
        "question": "Your question in natural language",
        "db_connection_id": "db_connection_id"
    }'
```

### Create new response based on a previously created question
After utilizing the `questions` endpoint, you have the option to generate a new response associated with a specific question_id. 
You can modify the `sql_query` to produce an alternative `sql_query_result` and a distinct response. In the event that you do not 
specify a `sql_query`, the system will reprocess the question to generate the `sql_query`, execute the `sql_query_result`, and subsequently 
generate the response.

```
curl -X 'POST' \
  '<host>/api/v1/responses?run_evaluator=true&sql_response_only=false&generate_csv=false' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question_id": "11fa1e419fe93d137536fe99",
  "sql_query": "select * from sales order by created_at DESC limit 10"
}'
```

### Run scripts
Within the `scripts` folder located inside the `dataherald` directory, you have the ability to upgrade your versions. 
For instance, if you are currently using version 0.0.3 and wish to switch to version 0.0.4, simply execute the following command:

```
docker-compose exec app python3 -m dataherald.scripts.migrate_v003_to_v004
```
Additionally, we provide a script for managing the Vector Store data. You can delete the existing data and upload all 
the Golden Records to the 'golden_records' collection in MongoDB. If you are utilizing `Chroma` in-memory storage, it's 
important to note that data is lost upon container restart. To repopulate the data, execute the following command:

```
docker-compose exec app python3 -m dataherald.scripts.delete_and_populate_golden_records
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


### Mongo errors

The Mongo installation is configured to store application data in the `/dbdata` folder. In case you want to wipe the local DB, try completely deleting `/dbdata` before rebuilding the databases.

