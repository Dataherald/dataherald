.. api.scan_database:

Get a table description
=======================

This endpoint returns a table description

Request this ``GET`` endpoint::

   /api/v1/table-descriptions/<table_description_id>


**Responses**

HTTP 200 code response

.. code-block:: rst

  {
    "id": "string",
    "db_connection_id": "string",
    "table_name": "string",
    "description": "string",
    "table_schema": "string",
    "status": "NOT_SCANNED | SYNCHRONIZING | DEPRECATED | SCANNED | FAILED"
    "error_message": "string",
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


.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "status", "string", "It can be one of the next options:
    - `NOT_SCANNED` if the table has not been scanned
    - `SYNCHRONIZING` while the sync schema process is running
    - `DEPRECATED` if there is a row in our `table-descriptions` collection that is no longer in the database, probably because the table/view was deleted or renamed
    - `SCANNED` when we have scanned the table
    - `FAILED` if anything failed during the sync schema process, and the `error_message` field stores the error."
   "error_message", "string", "This field is set only if the async schema process fails"


**Request example**

.. code-block:: rst

    curl -X 'GET' \
      '<localhost>/api/v1/table-descriptions/64fa09446cec0b4ff60d3ae3 \
      -H 'accept: application/json'
