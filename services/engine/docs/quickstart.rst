Quick Start
============

The easiest way to self-host the engine is using Docker. By default, the engine will start in a docker instance with another docker instance running Mongo to store application data.

Setting Environment Variables
------------------------------
In order for the Dataherald engine to run, you must set the following environment variables in the .env file in the root folder. You can use some of the default values in the .env.example file.


``cp .env.example .env``

The following environment variables must be set manually before the engine is started, otherwise the engine will not start.


.. code-block:: rst

    #OpenAI credentials and model 
    OPENAI_API_KEY = 
    ORG_ID =

    #Encryption key for storing DB connection data in Mongo
    ENCRYPT_KEY = 

The ``ENCRYPT_KEY`` is used to encrypt database connection data before storing it in Mongo. You can generate a key from the command line terminal using the following

.. code-block:: rst

    pip3 install cryptography

    # Run python in terminal
    python3

    # Import Fernet
    from cryptography.fernet import Fernet

    # Generate the key
    Fernet.generate_key()


While not strictly required, we also strongly suggest you change the MONGO username and password as well in the ``MONGODB_DB_USERNAME``, ``MONGODB_DB_PASSWORD`` and ``MONGODB_URI`` fields before start-up.

Starting Docker
----------------
#. Make sure you have Docker installed on your machine. You can download it from `here <https://www.docker.com/products/docker-desktop>`_

#. Create a Docker network for communication between services (the Dataherald engine and Mongo) using the following command 

    ```docker network create dataherald_network```


#. Build the docker images, create containers and raise them by running

    ```docker-compose up --build```

    You can skip the `--build` if you don't have to rebuild the image due to updates to the dependencies

#. Check that the containers are running by running ```docker ps```. You should see something like the following:

    .. code-block:: rst
        
        CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS         PORTS                      NAMES
        72aa8df0d589   dataherald-app   "uvicorn dataherald.…"   7 seconds ago   Up 6 seconds   0.0.0.0:80->80/tcp         dataherald-app-1
        6595d145b0d7   mongo:latest     "docker-entrypoint.s…"   19 hours ago    Up 6 seconds   0.0.0.0:27017->27017/tcp   mongodb


#. You can also verify the engine is running by navigating to the Swagger-UI from your browser at `<http://localhost/docs>`_




Using the Engine 
---------------------------------------
Once the engine is running, you will want to use it by:

#. Connecting to you data warehouses
#. Adding context about the data to the engine
#. Querying the data in natural language


Connecting to your Data Warehouse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We currently support connections to PostGres, BigQuery, Databricks and Snowflake. You can create connections to these warehouses through the API or at application start-up using the envars.

You can define a DB connection through a call to the following API endpoint `/api/v1/database`. For example 


    .. code-block:: rst

        curl -X 'POST' \
        '<host>/api/v1/database' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
            "db_connection_id": "db_connection_id",
            "use_ssh": false,
            "connection_uri": "sqlite:///mydb.db"
        }'


If you need to connect to your database through an SSH tunnel, you will need to set the ssh fields in the API call similar to below


    .. code-block:: rst

        curl -X 'POST' \
        'http://localhost/api/v1/database' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "db_connection_id": "db_connection_id",
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

Adding context to the engine 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While you can start querying in natural language your data warehouse after adding a connection, the generated SQL will likely not be very accurate until you start adding some context about the business logic and data to the context store. Dataherald allows you to do this in three ways:

#. Scanning the Database tables and columns using the `scanner <api.scan_database.html>`_
#. Adding verified SQL to be used in few shot prompting `also referred to as Golden SQL <api.golden_record.html>`_
#. Adding string descriptions of the tables and columns through the add_description `endpoint <api.add_descriptions.html>`_ 

The details of how to use these endpoints are outside the scope of this quickstart guide. Please refer to the API documentation from the links above for more information.

Querying the Database in Natural Language 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have connected the engine to your data warehouse (and preferably added some context to the store), you can query your data warehouse using the ``POST /api/v1/questions`` endpoint.

    .. code-block:: rst

        curl -X 'POST' \
        '<host>/api/v1/questions' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
                "question": "what was the most expensive zip code to rent in Los Angeles county in May 2022?"",
                "db_connection_id": "db_connection_id"
            }'


... and *voila* you can now start using Dataherald to query your data warehouse in natural language.





