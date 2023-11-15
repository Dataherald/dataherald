.. _api.list_instructions:

List instructions
=======================

You can use this endpoint to retrieve a list of instructions for a database connection.

Request this ``GET`` endpoint::

    GET /api/v1/instructions

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_connection_id", "string", "Database connection we want to get instructions, ``Optional``"
   "page", "integer", "Page number, ``Optional``"
   "limit", "integer", "Limit number of instructions, ``Optional``"

**Responses**

HTTP 201 code response

.. code-block:: rst

    [
        {
            "id": "string",
            "instruction": "string",
            "db_connection_id": "string"
        }
    ]

**Example**

.. code-block:: rst

   curl -X 'GET' \
  '<host>/api/v1/instructions?page=1&limit=10&db_connection_id=12312312' \
  -H 'accept: application/json

