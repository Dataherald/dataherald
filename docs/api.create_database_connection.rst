Create a Database connection
=============================

We currently support connections to the following data warehouses: ``databricks``, ``postgresql``, ``snowflake``, ``bigquery`` and ``AWS Athena``. All sensitive connection data
is encrypted using the key you provide in your .env file before being stored to the application storage. 

You can also specify the engine to connect to the Database through an SSH tunnel, as demonstrated in the second example below.

You can find additional details on how to connect to each of the supported data warehouses :ref:`below <Supported Data warehouses>`.


**Request this POST endpoint**::

   /api/v1/database-connections

**Request body**

.. code-block:: rst

   {
      "alias": "string",
      "use_ssh": true,
      "connection_uri": "string",
      "path_to_credentials_file": "string",
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

**SSH Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

    "db_name", "string", "The name of the database you want to connect to"
    "host", "string", "The hostname or IP address of the SSH server you need to access"
    "username", "string", "Your username for SSH authentication"
    "password", "string", "Your password for SSH authentication"
    "remote_host", "string", "The hostname or IP address of the remote database server you want to connect to."
    "remote_db_name", "string", "The name of the remote database you want to interact with."
    "remote_db_password", "string", "The password for accessing the remote database."
    "private_key_path", "string", "The file path to locate your id_rsa private key file. For example, if you are using Docker and the file is located at the root, the path would be /app/id_rsa. Ensure that you include this file in your Docker container by building it."
    "private_key_password", "string", "The password for the id_rsa private key file, if it is password-protected"
    "db_driver", "string", "Set the database driver. For example, for PostgreSQL, the driver should be set to `postgresql+psycopg2`"

**Responses**

HTTP 200 code response

.. code-block:: rst

    {
      "id": "64f251ce9614e0e94b0520bc",
      "alias": "string_999",
      "use_ssh": false,
      "uri": "gAAAAABk8lHQNAUn5XARb94Q8H1OfHpVzOtzP3b2LCpwxUsNCe7LGkwkN8FX-IF3t65oI5mTzgDMR0BY2lzvx55gO0rxlQxRDA==",
      "path_to_credentials_file": "string",
      "ssh_settings": {
        "db_name": "string",
        "host": "string",
        "username": "string",
        "password": "gAAAAABk8lHQAaaSuoUKxddkMHw7jerwFmUeiE3hL6si06geRt8CV-r43fbckZjI6LbIULWPZ4HlQUF9_YpfaYfM6FarQbhDUQ==",
        "remote_host": "string",
        "remote_db_name": "string",
        "remote_db_password": "gAAAAABk8lHQpZyZ6ow8EuYPWe5haP-roQbBWkZn3trLgdO632IDoKcXAW-8yjzDDQ4uH03iWFzEgJq8HRxkJTC6Ht7Qrlz2PQ==",
        "private_key_path": "string",
        "private_key_password": "gAAAAABk8lHQWilFpIbCADvunHGYFMqgoPKIml_WRXf5Yuowqng28DVsq6-sChl695y5D_mWrr1I3hcJCZqkmhDqpma6iz3PKA==",
        "db_driver": "string"
      }
    }

HTTP 400 code response (if the db connection fails it returns a 400 error)

.. code-block:: rst

    {
        "detail": "string"
    }

**Example 1**

Without a SSH connection

.. code-block:: rst

   curl -X 'POST' \
      '<host>/api/v1/database-connections' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "alias": "my_db_alias_identifier",
      "use_ssh": false,
      "connection_uri": "sqlite:///mydb.db"
    }'

**Example 2**

With a SSH connection

.. code-block:: rst

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

Specify a schema (If it isn't specified by default it uses `public`)::

"connection_uri": postgresql+psycopg2://<user>:<password>@<host>:<port>/<db-name>?options=-csearch_path=<my-schema>

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

AWS Athena
^^^^^^^^^^^^

Uri structure::

"connection_uri": awsathena+rest://<aws_access_key_id>:<aws_secret_access_key>@athena.<region_name>.amazonaws.com:443/<schema_name>?s3_staging_dir=<s3_staging_dir>&work_group=primary

Example::

"connection_uri": awsathena+rest://foobar:foobar@athena.us-east-2.amazonaws.com:443/db_test?s3_staging_dir=s3://my-bucket/output/&work_group=primary

BigQuery
^^^^^^^^^^^^

To connect to BigQuery you should create a json credential file. Please follow Steps 1-3 under "Configure BigQuery
Authentication in Google Cloud Platform" in
this `tutorial <https://www.privacydynamics.io/docs/connections/bigquery.html>`_.

    Please ensure the service account only has **"Viewer"** permissions.

Once you have your credential json file you can store it inside the project. For example given the credential file `my-db-123456acbd.json` 
in the folder `private_credentials`  you should set in the endpoint param `path_to_credentials_file` the path, for example::

    "path_to_credentials_file": "private_credentials/my-db-123456acbd.json"


and the ``connection_uri`` will be:

Uri structure::

"connection_uri": bigquery://<project>/<database>

Example::

"connection_uri": bigquery://v2-real-estate/K2


