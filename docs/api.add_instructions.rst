.. _api.add_instructions:

Set Instructions
=======================

To return an accurate response based on our your business rules, you can set some constraints on the SQL generation process.

Request this ``POST`` endpoint::

    /api/v1/instructions

**Request body**

.. code-block:: rst

   {
    "instruction": "string"
    "db_connection_id": "database_connection_id"
   }

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
    "id": "instruction_id",
    "instruction": "Instructions",
    "db_connection_id": "database_connection_id"
    }

**Example**

Only set a instruction for a database connection

.. code-block:: rst

   curl -X 'POST' \
  '<host>/api/v1/instructions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "instruction": "string",
  "db_connection_id": "database_connection_id"
   }'

