Environment Variables
=======================
The Dataherald engine has a number of environment variables that need to be set in order for it to work. The following is the sample
provided in the .env.example file with the default values. 


.. code-block:: bash

    OPENAI_API_KEY = 
    ORG_ID =


    GOLDEN_RECORD_COLLECTION = 'my-golden-records'
    PINECONE_API_KEY =
    PINECONE_ENVIRONMENT =

    ASTRA_DB_API_ENDPOINT =
    ASTRA_DB_APPLICATION_TOKEN =

   
    API_SERVER = "dataherald.api.fastapi.FastAPI"
    SQL_GENERATOR = "dataherald.sql_generator.dataherald_sqlagent.DataheraldSQLAgent"
    EVALUATOR = "dataherald.eval.simple_evaluator.SimpleEvaluator"
    DB = "dataherald.db.mongo.MongoDB"
    VECTOR_STORE = 'dataherald.vector_store.chroma.Chroma' 
    CONTEXT_STORE = 'dataherald.context_store.default.DefaultContextStore' 
    DB_SCANNER = 'dataherald.db_scanner.sqlalchemy.SqlAlchemyScanner'


    MONGODB_URI = "mongodb://admin:admin@mongodb:27017"
    MONGODB_DB_NAME = 'dataherald'
    MONGODB_DB_USERNAME = 'admin'
    MONGODB_DB_PASSWORD = 'admin'

    ENCRYPT_KEY = 

    S3_AWS_ACCESS_KEY_ID =
    S3_AWS_SECRET_ACCESS_KEY =
  
    ONLY_STORE_CSV_FILES_LOCALLY =

    MINIO_ROOT_USER =
    MINIO_ROOT_PASSWORD =

    AGENT_MAX_ITERATIONS = 15
    DH_ENGINE_TIMEOUT = 150
    SQL_EXECUTION_TIMEOUT = 30
    UPPER_LIMIT_QUERY_RETURN_ROWS = 50

    CORE_PORT = 

    EMBEDDING_MODEL = "text-embedding-3-large"

.. csv-table::
   :header: "Variable Name", "Description", "Default Value", "Required"
   :widths: 15, 55, 25, 5

   "OPENAI_API_KEY", "The OpenAI key used by the Dataherald Engine", "None", "Yes"
   "ORG_ID", "The OpenAI Organization ID used by the Dataherald Engine", "None", "Yes"
   "GOLDEN_RECORD_COLLECTION", "The name of the collection in Mongo where golden records will be stored", "``my-golden-records``", "No"
   "PINECONE_API_KEY", "The Pinecone API key used", "None", "Yes if using the Pinecone vector store"
   "PINECONE_ENVIRONMENT", "The Pinecone environment", "None", "Yes if using the Pinecone vector store"
   "ASTRA_DB_API_ENDPOINT", "The Astra DB API endpoint", "None", "Yes if using the Astra DB"
   "ASTRA_DB_APPLICATION_TOKEN", "The Astra DB application token", "None", "Yes if using the Astra DB
   "API_SERVER", "The implementation of the API Module used by the Dataherald Engine.", "``dataherald.api.fastapi.FastAPI``", "Yes"
   "SQL_GENERATOR", "The implementation of the SQLGenerator Module to be used.", "``dataherald.sql_generator.  dataherald_sqlagent. DataheraldSQLAgent``", "Yes"
   "EVALUATOR", "The implementation of the Evaluator Module to be used.", "``dataherald.eval. simple_evaluator.SimpleEvaluator``", "Yes"
   "DB", "The implementation of the DB Module to be used.", "``dataherald.db.mongo.MongoDB``", "Yes"
   "VECTOR_STORE", "The implementation of the Vector Store Module to be used. Chroma and Pinecone modules are currently included.", "``dataherald.vector_store. chroma.Chroma``", "Yes"
   "CONTEXT_STORE", "The implementation of the Context Store Module to be used.", "``dataherald.context_store. default.DefaultContextStore``", "Yes"
   "DB_SCANNER", "The implementation of the DB Scanner Module to be used.", "``dataherald.db_scanner. sqlalchemy.SqlAlchemyScanner``", "Yes"
   "MONGODB_URI", "The URI of the MongoDB that will be used for application storage.", "``mongodb:// admin:admin@mongodb:27017``", "Yes"
   "MONGODB_DB_NAME", "The name of the MongoDB database that will be used.", "``dataherald``", "Yes"
   "MONGODB_DB_USERNAME", "The username of the MongoDB database", "``admin``", "Yes"
   "MONGODB_DB_PASSWORD", "The password of the MongoDB database", "``admin``", "Yes"
   "ENCRYPT_KEY", "The key that will be used to encrypt data at rest before storing", "None", "Yes"
   "S3_AWS_ACCESS_KEY_ID", "The key used to access credential files if saved to S3", "None", "No"
   "S3_AWS_SECRET_ACCESS_KEY", "The key used to access credential files if saved to S3", "None", "No"
   "DH_ENGINE_TIMEOUT", "This is used to set the max seconds the process will wait for the response to be generate. If the specified time limit is exceeded, it will trigger an exception", "``150``", "No"
   "SQL_EXECUTION_TIMEOUT", "This is the timeout for SQL execution, our agents execute the SQL query to recover from errors, this is the timeout for that execution. If the specified time limit is exceeded, it will trigger an exception", "``60``", "No"
   "UPPER_LIMIT_QUERY_RETURN_ROWS", "The upper limit on number of rows returned from the query engine (equivalent to using LIMIT N in PostgreSQL/MySQL/SQlite).", "None", "No"
   "ONLY_STORE_CSV_FILES_LOCALLY", "Set to True if only want to save generated CSV files locally instead of S3. Note that if stored locally they should be treated as ephemeral, i.e., they will disappear when the engine is restarted.", "None", "No"
   "MINIO_ROOT_USER","The username of the MinIO service.","None","No"
   "MINIO_ROOT_PASSWORD","The password of the MinIO service.","None","No"
   "CORE_PORT","The port that will be used by the container to run the engine. Make sure to bind the core port with the desired local port.","``80``","No"
   "EMBEDDING_MODEL","The name of the embedding model used. If you are using OpenAI, use text-embedding-3-large. If you are using deployed service, make sure to use the name of the deployed embedding model","``text-embedding-3-large``","No"
