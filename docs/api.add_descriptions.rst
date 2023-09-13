.. _api.add_descriptions:

Set descriptions
=======================

To return an accurate response set descriptions per table and column.

Request this ``PATCH`` endpoint::

   /api/v1/table-descriptions/{table_description_id}


**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "table_description_id", "String", "Table description id, ``Required``"

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

    {
      "id": "string",
      "db_connection_id": "string",
      "table_name": "string",
      "description": "string",
      "table_schema": "string",
      "columns": [
        {
          "name": "string",
          "is_primary_key": false,
          "data_type": "str",
          "description": "string",
          "low_cardinality": false,
          "categories": [
            "string"
          ],
          "foreign_key": {
            "field_name": "string",
            "reference_table": "string"
          }
        }
      ],
      "examples": []
    }

**Example 1**

Only set a table description

.. code-block:: rst

   curl -X 'PATCH' \
  '<host>/api/v1/table-descriptions/64fa09446cec0b4ff60d3ae3' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
        "description": "Only set a table description"
    }'

**Example 2**

Only set columns descriptions

.. code-block:: rst

   curl -X 'PATCH' \
  '<host>/api/v1/table-descriptions/64fa09446cec0b4ff60d3ae3' \
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


