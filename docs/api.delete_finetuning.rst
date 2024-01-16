.. _api.delete_finetuning:

Delete Finetuning
=======================

If you want to delete a finetuning, you can use this endpoint.

Request this ``DELETE`` endpoint::

    /api/v1/finetunings/<finetuning_id>

** Parameters **

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "finetuning_id", "string", "Finetuning id we want to delete, ``Required``"

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
    "status": bool,
    }

**Example**

Delete finetuning with id ``5e8b4a1c-4b0c-4b0c-8b4a-1c4b0c8b4a1c``

.. code-block:: rst

   curl -X 'DELETE' \
  '<host>/api/v1/finetunings/5e8b4a1c-4b0c-4b0c-8b4a-1c4b0c8b4a1c' \
  -H 'accept: application/json'

