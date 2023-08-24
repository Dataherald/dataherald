Create a Database connection
=============================

We currently support connections to the following data warehouses: ``databricks``, ``postgresql``, ``snowflake``, ``bigquery``. All sensitive connection data 
is encrypted using the key you provide in your .env file before being stored to the application storage. 

You can also specify the engine to connect to the Database through an SSH tunnel, as demonstrated in the second example below.

You can find additional details on how to connect to each of the supported data warehouses :ref:`below <Supported Data warehouses>`.


**Request this POST endpoint**::

   /api/v1/database

**Request body**

.. code-block:: rst

   {
      "db_alias": "string",
      "use_ssh": true,
      "connection_uri": "string",
      "ssh_settings": {
        "db_name": "string",
        "host": "string",
        "username": "string",
        "password": "string",
        "remote_host": "string",
        "remote_db_name": "string",
        "remote_db_password": "string",
        "private_key_path": "string",
        "private_key_password": "string",
        "db_driver": "string"
      }
    }

**Responses**

HTTP 200 code response

.. code-block:: rst

    true

**Example 1**

Without a SSH connection

.. code-block:: rst

   curl -X 'POST' \
      '<host>/api/v1/database' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "db_alias": "my_db_alias_identifier",
      "use_ssh": false,
      "connection_uri": "sqlite:///mydb.db"
    }'

**Example 2**

With a SSH connection

.. code-block:: rst

    curl -X 'POST' \
      'http://localhost/api/v1/database' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "db_alias": "my_db_alias_identifier",
      "use_ssh": true,
      "ssh_settings": {
        "db_name": "db_name",
        "host": "string",
        "username": "string",
        "password": "string",
        "remote_host": "string",
        "remote_db_name": "string",
        "remote_db_password": "string",
        "private_key_path": "string",
        "private_key_password": "string",
        "db_driver": "string"
      }
    }'


.. _Supported Data warehouses: 

Connections to supported Data warehouses
-----------------------------------------

The format of the ``connection_uri`` parameter in the API call will depend on the data warehouse type you are connecting to. 
You can find samples and how to generate them :ref:<below >. 

Postgres
^^^^^^^^^^^^

Uri structure::

"connection_uri": postgresql+psycopg2://<user>:<password>@<host>:<port>/<db-name>

Example::

"connection_uri": postgresql+psycopg2://admin:123456@foo.rds.amazonaws.com:5432/my-database

Databricks
^^^^^^^^^^^^

Uri structure::

"connection_uri": databricks://token:<token>@<host>?http_path=<http-path>&catalog=<catalog>&schema=<schema-name>

Example::

"connection_uri": databricks://token:abcd1234abcd1234abcd1234abcd1234@foo-bar.cloud.databricks.com?http_path=sql/protocolv1/o/123456/123-1234-abcdabcd&catalog=foobar&schema=default

Snowflake
^^^^^^^^^^^^

Uri structure::

"connection_uri": snowflake://<user>:<password>@<organization>-<account-name>/<database>/<schema>

Example::

"connection_uri": snowflake://jon:123456@foo-bar/my-database/public


BigQuery
^^^^^^^^^^^^

To connect to BigQuery you should create a json credential file. You can
follow this `tutorial <https://www.privacydynamics.io/docs/connections/bigquery.html>`_ to generate it.

Once you have your credential json file you can store it inside the project. For example given the credential file `my-db-123456acbd.json` 
in the folder `private_credentials` the ``connection_uri`` will be:

Uri structure::

"connection_uri": bigquery://<project>/<database>?credentials_path=<path-to-your-credential-file>

Example::

"connection_uri": bigquery://v2-real-estate/K2?credentials_path=./private_credentials/my-db-123456acbd.json


