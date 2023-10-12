.. api.scan_database:

Scan a Database
=======================

Once you have set your db credentials request this endpoint to scan your database. It maps
all tables and columns so It will help the SQL Agent to generate an accurate answer.

It can scan all db tables or if you specify a `table_names` then It will only scan those tables.

The process is carried out through Background Tasks, ensuring that even if it operates slowly, taking several minutes, the HTTP response remains swift.

Request this ``POST`` endpoint::

   /api/v1/table-descriptions/sync-schemas

**Request body**

.. code-block:: rst

   {
      "db_connection_id": "string",
      "table_names": ["string"] # Optional
    }

**Responses**

HTTP 201 code response

.. code-block:: rst

    true

**Request example**

To scan all the tables in a db don't specify a `table_names`

.. code-block:: rst

   curl -X 'POST' \
  '<localhost>/api/v1/table-descriptions/sync-schemas' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
      -d '{
      "db_connection_id": "db_connection_id"
    }'
