Create a Database connection
=======================

To create a database connection, currently it only supports these db managers
``databricks``, ``postgresql``, ``snowflake``, ``bigquery`` and databases behind a VPN using a SSH tunnel.
Besides all sensible data is encrypted using Fernet

Request this ``POST`` endpoint::

   /api/v1/database

**Request body**

.. code-block:: rst

   {
      "db_alias": "string",
      "use_ssh": true,
      "connection_uri": "string",
      "ssh_settings": {
        "db_name": "v2_real_estate",
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