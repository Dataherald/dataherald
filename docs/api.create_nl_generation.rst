Create a NL generation
=============================

NL generation is the resource that contains all of natural language response generated for SQL generations.

max_rows parameter defines how many rows after executing the SQL query should be used for NL generation.

Request this ``POST`` endpoint to create a NL generation for a given SQL generation::

    api/v1/sql-generations/{sql_generation_id}/nl-generations

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "sql_generation_id", "string", "the SQL generation id that we want to create NL response for, ``Required``"


**Request body**

.. code-block:: rst

   {
        "max_rows": 100,
        "metadata": {}
    }

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
        "id": "string",
        "metadata": {},
        "created_at": "string",
        "sql_generation_id": "string",
        "text": "string"
    }

**Request example**

.. code-block:: rst

    curl -X 'POST' \
    'http://localhost/api/v1/sql-generations/65971ec8d274e27e2a360457/nl-generations' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "max_rows": 100,
    "metadata": {}
    }'


**Response example**

.. code-block:: rst

    {
    "id": "659f1194fb38253f83458065",
    "metadata": {},
    "created_at": "2024-01-10 21:52:20.352826",
    "sql_generation_id": "65971ec8d274e27e2a360457",
    "text": "The most expensive zip code to rent in Los Angeles county in May 2022 was 91302, with the highest rent being $13,219.15."
    }