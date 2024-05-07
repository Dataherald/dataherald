List NL generations
============================

request this ``GET`` endpoint to get a list of NL generations.

    /api/v1/nl_generations

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "sql_generation_id", "string", "the sql generation id, ``Optional``"


**Responses**

HTTP 200 code response

.. code-block:: rst

    [
        {
            "id": "string",
            "metadata": {},
            "created_at": "string",
            "sql_generation_id": "string",
            "text": "string"
        }
    ]

**Request example**

.. code-block:: rst

   curl -X 'GET' \
  'http://localhost/api/v1/nl_generations' \
   -H 'accept: application/json'

**Response example**

.. code-block:: rst

    [
        {
            "id": "659f166dfb38253f8345806d",
            "metadata": {},
            "created_at": "2024-01-10 22:13:01.707000+00:00",
            "sql_generation_id": "659f1603fb38253f8345806c",
            "text": "The average rent price in LA is $3,337.42."
        }
    ]