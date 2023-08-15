Set descriptions
=======================

To return an accurate response set descriptions per table and column.

Request this ``PATCH`` endpoint::

   /api/v1/scanned-db/{db_name}/{table_name}


**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 15, 10, 30

   "db_name", "String", "Database name, ``Required``"
   "table_name", "String", "Table name, ``Required``"

**Request body**

.. code-block:: rst

   {
      "description": "string", #optional
      "columns": [ #optional
        {
          "name": "string",
          "description": "string"
        }
      ]
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


