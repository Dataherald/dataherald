Create a prompt and a SQL generation
============================================

This endpoint can be used to create a prompt and a SQL query at the same time. The prompt is used to generate the SQL query.
This endpoint has all of the parameters required for prompts and SQL generation.

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


Request this ``POST`` endpoint to create a SQL query and a NL response for a given prompt::

    api/v1/prompts/sql-generations


**Request body**

.. code-block:: rst

   {
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

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
        "id": "string",
        "metadata": {},
        "created_at": "string",
        "prompt_id": "string",
        "finetuning_id": "string",
        "status": "string",
        "completed_at": "string",
        "sql": "string",
        "tokens_used": 0,
        "confidence_score": 0,
        "error": "string"
    }

**Request example**

.. code-block:: rst

    curl -X 'POST' \
        'http://localhost/api/v1/prompts/sql-generations' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "evaluate": false,
        "metadata": {},
        "prompt": {
            "text": "What is the average rent price in LA?",
            "db_connection_id": "6595907efef5f74dd0069519",
            "metadata": {}
        }
    }'


**Response example**

.. code-block:: rst

    {
        "id": "659ffd2ffb38253f8345806f",
        "metadata": {},
        "created_at": "2024-01-11 14:37:35.170057",
        "prompt_id": "659ffd2ffb38253f8345806e",
        "finetuning_id": null,
        "status": "VALID",
        "completed_at": "2024-01-11 14:38:44.348818",
        "sql": "SELECT dh_state_name, location_name, metric_value\nFROM renthub_average_rent\nWHERE location_name = 'Los Angeles' -- Filter for Los Angeles\n  AND geo_type = 'city' -- Filter for city geo_type\n  AND property_type = 'All Residential' -- Filter for All Residential property type\n  AND metric_value IS NOT NULL -- Exclude rows where metric_value is NULL",
        "tokens_used": 11554,
        "confidence_score": null,
        "error": null
    }