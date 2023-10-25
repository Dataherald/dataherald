Update a Database connection
=============================

This endpoint is used to update a Database connection

**Request this PUT endpoint**::

   /api/v1/database-connections/{db_connection_id}

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_connection_id", "String", "Set the database connection id, ``Required``"

**Request body**

.. code-block:: rst

   {
      "alias": "string",
      "use_ssh": true,
      "connection_uri": "string",
      "path_to_credentials_file": "string",
      "llm_api_key": "string",
      "ssh_settings": {
        "db_name": "string",
        "host": "string",
        "username": "string",
        "password": "string",
        "remote_host": "string",
        "remote_db_name": "string",
        "remote_db_password": "string",
        "private_key_password": "string",
        "db_driver": "string"
      }
    }

**Responses**

HTTP 200 code response

.. code-block:: rst

    {
      "id": "64f251ce9614e0e94b0520bc",
      "alias": "string_999",
      "use_ssh": false,
      "uri": "gAAAAABk8lHQNAUn5XARb94Q8H1OfHpVzOtzP3b2LCpwxUsNCe7LGkwkN8FX-IF3t65oI5mTzgDMR0BY2lzvx55gO0rxlQxRDA==",
      "path_to_credentials_file": "string",
      "llm_api_key": "string",
      "ssh_settings": {
        "db_name": "string",
        "host": "string",
        "username": "string",
        "password": "gAAAAABk8lHQAaaSuoUKxddkMHw7jerwFmUeiE3hL6si06geRt8CV-r43fbckZjI6LbIULWPZ4HlQUF9_YpfaYfM6FarQbhDUQ==",
        "remote_host": "string",
        "remote_db_name": "string",
        "remote_db_password": "gAAAAABk8lHQpZyZ6ow8EuYPWe5haP-roQbBWkZn3trLgdO632IDoKcXAW-8yjzDDQ4uH03iWFzEgJq8HRxkJTC6Ht7Qrlz2PQ==",
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

   curl -X 'PUT' \
      '<host>/api/v1/database-connections/64f251ce9614e0e94b0520bc' \
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

    curl -X 'PUT' \
      '<host>/api/v1/database-connections/64f251ce9614e0e94b0520bc' \
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

**Example 3**

With a SSH connection and LLM credentials

.. code-block:: rst

    url -X 'POST' \
      '<host>/api/v1/database-connections' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "alias": "my_db_alias",
      "use_ssh": true,
      "llm_api_key": "api_key",
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

