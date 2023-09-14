.. api.scan_database:

List table descriptions
=======================

Once you have scanned a db connection you can list the table descriptions by requesting this endpoint.

Request this ``GET`` endpoint::

   /api/v1/table-descriptions

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_connection_id", "string", "Filter by connection id, ``Optional``"
   "table_name", "string", "Filter by table name, ``Optional``"

**Responses**

HTTP 200 code response

.. code-block:: rst

    [
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
    ]

**Request example**

.. code-block:: rst

    curl -X 'GET' \
      '<localhost>/api/v1/table-descriptions?db_connection_id=64fa09446cec0b4ff60d3ae3&table_name=foo' \
      -H 'accept: application/json'
