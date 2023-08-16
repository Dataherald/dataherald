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
    LLM_MODEL =      
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



Starting Docker
----------------
Make sure you have Docker installed on your machine. You can download it from [here](https://www.docker.com/products/docker-desktop)

Create a Docker network for communication between services (the Dataherald engine and Mongo) using the following command 

```docker network create backendnetwork```


Build the docker images, create containers and raise them by running

```docker-compose up --build```

You can skip the `--build` if you don't have to rebuild the image due to updates to the dependencies

Check that the containers are running by running

```docker ps```

You should see something like:

.. code-block:: rst
    CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS         PORTS                      NAMES
    72aa8df0d589   dataherald-app   "uvicorn dataherald.…"   7 seconds ago   Up 6 seconds   0.0.0.0:80->80/tcp         dataherald-app-1
    6595d145b0d7   mongo:latest     "docker-entrypoint.s…"   19 hours ago    Up 6 seconds   0.0.0.0:27017->27017/tcp   dataherald-mongodb-1


You can also verify the engine is running by navigating to the Swagger-UI from your browser at [http://localhost/docs](http://localhost/docs)




Using the Engine 
---------------------------------------







