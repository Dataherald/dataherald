Create a Database connection
=============================

To create a database connection, currently it only supports these db managers
``databricks``, ``postgresql``, ``snowflake``, ``bigquery`` and databases behind a VPN using a SSH tunnel.
Besides all sensible data is encrypted using Fernet

To generate the ``connection_uri`` param follow the next examples per every data warehouse that we support:

a) Postgres

Uri structure::

"connection_uri": postgresql+psycopg2://<user>:<password>@<host>:<port>/<db-name>

Example::

"connection_uri": postgresql+psycopg2://admin:123456@foo.rds.amazonaws.com:5432/my-database

b) Databricks

Uri structure::

"connection_uri": databricks://token:<token>@<host>?http_path=<http-path>&catalog=<catalog>&schema=<schema-name>

Example::

"connection_uri": databricks://token:abcd1234abcd1234abcd1234abcd1234@foo-bar.cloud.databricks.com?http_path=sql/protocolv1/o/123456/123-1234-abcdabcd&catalog=foobar&schema=default

c) Snowflake

Uri structure::

"connection_uri": snowflake://<user>:<password>@<organization>-<account-name>/<database>/<schema>

Example::

"connection_uri": snowflake://jon:123456@foo-bar/my-database/public


d) BigQuery

To connect to BigQuery you should create a credential file, this is a json file, you can
follow this [tutorial](https://www.privacydynamics.io/docs/connections/bigquery.html) to generate it.

Once you have your credential json file you can store it inside this project for example I created the folder
`private_credentials` and inside I stored my credential file `my-db-123456acbd.json`

Uri structure::

"connection_uri": bigquery://<project>/<database>?credentials_path=<path-to-your-credential-file>

Example::

"connection_uri": bigquery://v2-real-estate/K2?credentials_path=./private_credentials/my-db-123456acbd.json


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