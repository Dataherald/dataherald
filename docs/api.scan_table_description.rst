.. api.scan_database:

Create a table description
=======================

Once you have set your db credentials request this endpoint to scan your database. It maps
all tables and columns so It will help the SQL Agent to generate an accurate answer. In addition, it retrieves logs,
which consist of historical queries associated with each database table. These records are then stored within the
query_history collection. The historical queries retrieved encompass data from the past three months and are grouped
based on query and user.

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
