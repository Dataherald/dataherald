Environment Variables
=======================
The Dataherald engine has a number of environment variables that need to be set in order for it to work. The following is the sample
provided in the .env.example file with the default values. 


.. code-block:: bash

    OPENAI_API_KEY = 
    ORG_ID =
    LLM_MODEL = 'gpt-4-32k' 


    GOLDEN_RECORD_COLLECTION = 'my-golden-records'
    PINECONE_API_KEY =
    PINECONE_ENVIRONMENT =

   
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

    DH_ENGINE_TIMEOUT =
    UPPER_LIMIT_QUERY_RETURN_ROWS =


.. csv-table::
   :header: "Variable Name", "Description", "Default Value", "Required"
   :widths: 15, 55, 25, 5

   "OPENAI_API_KEY", "The OpenAI key used by the Dataherald Engine", "None", "Yes"
   "ORG_ID", "The OpenAI Organization ID used by the Dataherald Engine", "None", "Yes"
   "LLM_MODEL", "The Language Model used by the Dataherald Engine. Supported values include gpt-4-32k, gpt-4, gpt-3.5-turbo, gpt-3.5-turbo-16k", "``gpt-4-32k``", "No"
   "GOLDEN_RECORD_COLLECTION", "The name of the collection in Mongo where golden records will be stored", "``my-golden-records``", "No"
   "PINECONE_API_KEY", "The Pinecone API key used", "None", "Yes if using the Pinecone vector store"
   "PINECONE_ENVIRONMENT", "The Pinecone environment", "None", "Yes if using the Pinecone vector store"
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
   "DH_ENGINE_TIMEOUT", "This is used to set the max seconds the process will wait for the response to be generate. If the specified time limit is exceeded, it will trigger an exception", "None", "No"
   "UPPER_LIMIT_QUERY_RETURN_ROWS", "The upper limit on number of rows returned from the query engine (equivalent to using LIMIT N in PostgreSQL/MySQL/SQlite).", "None", "No"
   "ONLY_STORE_CSV_FILES_LOCALLY", "Set to True if only want to save generated CSV files locally instead of S3. Note that if stored locally they should be treated as ephemeral, i.e., they will disappear when the engine is restarted.", "None", "No"

