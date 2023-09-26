.. _api.update_instructions:

Update Instructions
=======================

In order to get the best performance from the engine you should try using different instructions for each database connection.
You can update the instructions for a database connection using the ``PATCH`` method.

Request this ``PATCH`` endpoint::

    /api/v1/{db_connection_id}/instructions/{instruction_id}

** Parameters **

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_connection_id", "string", "Database connection we want to update the instructions, ``Required``"
    "instruction_id", "string", "Instruction id we want to update, ``Required``"

**Request body**

.. code-block:: rst

   {
    "instruction": "string"
   }

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
    "id": "string",
    "instruction": "string",
    "db_connection_id": "string"
    }

**Example**

Only set a instruction for a database connection

.. code-block:: rst

   curl -X 'PATCH' \
  '<host>/api/v1/{db_connection_id}/instructions/{instruction_id}' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "instruction": "string"
  }'

