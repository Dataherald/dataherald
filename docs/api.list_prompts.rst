.. _api.list_prompts:

List prompts
===========================

You can use this endpoint to retrieve a list of prompts for a given database connection.

Request this ``GET`` endpoint::

    GET /api/v1/prompts

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_connection_id", "string", "Database connection we want to get prompts, ``Optional``"

**Responses**

HTTP 201 code response

.. code-block:: rst

    [
        {
            "id": "string",
            "metadata": {},
            "created_at": "string",
            "text": "string",
            "db_connection_id": "string",
            "schemas": [
                "string"
            ]
        }
    ]

**Example**

.. code-block:: rst

   curl -X 'GET' \
  '<host>/api/v1/prompts?db_connection_id=12312312' \
  -H 'accept: application/json
