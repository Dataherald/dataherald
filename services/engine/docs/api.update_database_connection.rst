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
        "host": "string",
        "username": "string",
        "password": "string",
        "private_key_password": "string"
      }
    }

**Responses**

HTTP 200 code response

.. code-block:: rst

    {
      "id": "64f251ce9614e0e94b0520bc",
      "alias": "string_999",
      "dialect": "sqlite",
      "use_ssh": false,
      "connection_uri": "gAAAAABk8lHQNAUn5XARb94Q8H1OfHpVzOtzP3b2LCpwxUsNCe7LGkwkN8FX-IF3t65oI5mTzgDMR0BY2lzvx55gO0rxlQxRDA==",
      "path_to_credentials_file": "string",
      "llm_api_key": "string",
      "ssh_settings": {
        "host": "string",
        "username": "string",
        "password": "gAAAAABk8lHQAaaSuoUKxddkMHw7jerwFmUeiE3hL6si06geRt8CV-r43fbckZjI6LbIULWPZ4HlQUF9_YpfaYfM6FarQbhDUQ==",
        "private_key_password": "gAAAAABk8lHQWilFpIbCADvunHGYFMqgoPKIml_WRXf5Yuowqng28DVsq6-sChl695y5D_mWrr1I3hcJCZqkmhDqpma6iz3PKA=="
      }
    }

HTTP 400 code response (if the db connection fails it returns a 400 error), :doc:`here <api.error_codes>` you can find
all the error codes

.. code-block:: rst

    {
      "error_code": "string",
      "message": "string",
      "description": "string",
      "detail": {
        "alias": "string",
        "use_ssh": false,
        "connection_uri": "string"
      }
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
      "connection_uri": "gAAAAABk8lHQNAUn5XARb94Q8H1OfHpVzOtzP3b2LCpwxUsNCe7LGkwkN8FX-IF3t65oI5mTzgDMR0BY2lzvx55gO0rxlQxRDA==",
      "ssh_settings": {
        "host": "string",
        "username": "string",
        "password": "string",
        "private_key_password": "string"
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
      "connection_uri": "gAAABABk8lHQNAUn5XARb94Q8H1OfHpVzOtzP3b2LCpwxUsNCe7LGkwkN8FX-IF3t65oI5mTzgDMR0BY2lzvx55gO0rxlQxRDA==",
      "llm_api_key": "api_key",
      "ssh_settings": {
        "host": "string",
        "username": "string",
        "password": "string",
        "private_key_password": "string"
      }
    }'

