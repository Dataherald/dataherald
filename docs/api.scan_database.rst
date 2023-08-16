.. api.scan_database:

Scan a Database
=======================

Once you have set your db credentials request this endpoint to scan your database. It maps
all tables and columns so It will help the SQL Agent to generate an accurate answer.

It can scan all db tables or if you specify a `table_name` then It will only scan that table.

Request this ``POST`` endpoint::

   /api/v1/scanner

**Request body**

.. code-block:: rst

   {
      "db_alias": "string",
      "table_name": "string" # Optional
    }

**Responses**

HTTP 200 code response

.. code-block:: rst

    true

**Request example**

To scan all the tables in a db don't specify a `table_name`

.. code-block:: rst

   curl -X 'POST' \
  '<localhost>/api/v1/scanner' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
      -d '{
      "db_alias": "db_alias"
    }'
