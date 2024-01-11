Create a prompt, a SQL query and NL response
============================================

This endpoint can be used to create a prompt, a SQL query and NL response at the same time. The prompt is used to generate the SQL query and the SQL query is used to generate the NL response.
This endpoint has all of the parameters required for prompts, SQL generation, and NL generation.

NL generation parameters
------------------------

The following parameters are used for NL generation:

* max_rows: the maximum number of rows to return in the NL response

SQL generation parameters
-------------------------

The following parameters are used for SQL generation:

* finetuning_id: the id of the finetuning model. If this is not provided we use a reasoning LLM with retrieval augmented generation. If specified we use the finetuning model for sql generation.
* evaluate: whether to evaluate the generated SQL query.
* sql: if you want to manually create the SQL query you can provide it here. If this is not provided we use the prompt to generate the SQL query.

Prompt parameters
-----------------

The following parameters are used for prompts:

* text: the prompt text
* db_connection_id: the id of the database connection


Request this ``POST`` endpoint to create a SQL query, a NL response, and a given prompt::

    api/v1/prompts/sql-generations/nl-generations


**Request body**

.. code-block:: rst

   {
        "max_rows": 100,
        "metadata": {},
        "sql_generation": {
            "finetuning_id": "string",
            "evaluate": false,
            "sql": "string",
            "metadata": {},
            "prompt": {
            "text": "string",
            "db_connection_id": "string",
            "metadata": {}
            }
        }
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
        'http://localhost/api/v1/prompts/sql-generations/nl-generations' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "max_rows": 100,
        "metadata": {},
        "sql_generation": {
            "evaluate": false,
            "metadata": {},
            "prompt": {
            "text": "What is the average rent price in LA?",
            "db_connection_id": "6595907efef5f74dd0069519",
            "metadata": {}
            }
        }
    }'


**Response example**

.. code-block:: rst

    {
    "id": "659f166dfb38253f8345806d",
    "metadata": {},
    "created_at": "2024-01-10 22:13:01.707573",
    "sql_generation_id": "659f1603fb38253f8345806c",
    "text": "The average rent price in LA is $3,337.42."
    }