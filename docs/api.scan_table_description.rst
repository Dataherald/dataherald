.. api.scan_database:

Scan a Database
=======================

Once you have set your db credentials request this endpoint to scan your database. It maps
all tables and columns so It will help the SQL Agent to generate an accurate answer.

It can scan all db tables or if you specify a `table_names` then It will only scan those tables.

Request this ``POST`` endpoint::

   /api/v1/table-descriptions/scan

**Request body**

.. code-block:: rst

   {
      "db_connection_id": "string",
      "table_names": ["string"] # Optional
    }

**Responses**

HTTP 200 code response

.. code-block:: rst

    true

**Request example**

To scan all the tables in a db don't specify a `table_names`

.. code-block:: rst

   curl -X 'POST' \
  '<localhost>/api/v1/scanner' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
      -d '{
      "db_connection_id": "db_connection_id"
    }'
