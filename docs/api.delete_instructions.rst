.. _api.delete_instructions:

Delete Instructions
=======================

If your business logic requires to delete a instruction, you can use this endpoint.

Request this ``DELETE`` endpoint::

    /api/v1/instructions/{instruction_id}

** Parameters **

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "instruction_id", "string", "Instruction id we want to delete, ``Required``"

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
    "status": bool,
    }

**Example**

Only set a instruction for a database connection

.. code-block:: rst

   curl -X 'DELETE' \
  '<host>/api/v1/instructions/{instruction_id}' \
  -H 'accept: application/json'

