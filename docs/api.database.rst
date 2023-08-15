Create a Database connection
=======================

To create a database connection, currently it only supports these db managers
`databricks`, `postgresql`, `snowflake`, `bigquery` and databases behind a VPN using a SSH tunnel.

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

Only set a table description

.. code-block:: rst

   curl -X 'PATCH' \
  '<host>/api/v1/scanned-db/foo_db/foo_table' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
        "description": "Only set a table description"
    }'

**Example 2**

Only set columns descriptions

.. code-block:: rst

   curl -X 'PATCH' \
  '<host>/api/v1/scanned-db/foo_db/foo_table' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
      "columns": [
        {
          "name": "column1",
          "description": "Set column1 description"
        },
        {
          "name": "column2",
          "description": "Set column2 description"
        }
      ]
    }'
