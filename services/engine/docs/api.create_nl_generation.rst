Create a NL generation
=============================

NL generation is the resource that contains all of natural language response generated for SQL generations.

max_rows parameter defines how many rows after executing the SQL query should be used for NL generation.
llm_config is the configuration for the language model that will be used for NL generation. If you want to use open-source LLMs you should provide the api_base and llm_name. If you want to use OpenAI models don't specify api_base.

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
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview",
            "api_base": "string"
        },
        "max_rows": 100,
        "metadata": {}
    }

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
        "id": "string",
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview",
            "api_base": "string"
        },
        "metadata": {},
        "created_at": "string",
        "sql_generation_id": "string",
        "text": "string"
    }

**Request example**

.. code-block:: rst

    curl -X 'POST' \
    'http://localhost/api/v1/sql-generations/65babe4335db7cdd1094c14d/nl-generations' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "llm_config": {
        "llm_name": "gpt-4-turbo-preview"
    },
    "max_rows": 100,
    "metadata": {}
    }'


**Response example**

.. code-block:: rst

    {
    "id": "65bbaf66142cc9bea23e2a00",
    "metadata": {},
    "created_at": "2024-02-01T14:49:10.849609+00:00",
    "llm_config": {
        "llm_name": "gpt-4-turbo-preview",
        "api_base": null
    },
    "sql_generation_id": "65babe4335db7cdd1094c14d",
    "text": "I don't know."
    }