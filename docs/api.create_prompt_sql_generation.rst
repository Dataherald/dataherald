Create a prompt and a SQL generation
============================================

This endpoint can be used to create a prompt and a SQL query at the same time. The prompt is used to generate the SQL query.
This endpoint has all of the parameters required for prompts and SQL generation.

SQL generation parameters
-------------------------

The following parameters are used for SQL generation:

* finetuning_id: the id of the finetuning model. If this is not provided we use a reasoning LLM with retrieval augmented generation. If specified we use the finetuning model for sql generation.
* low_latency_mode: When this flag is set, some of the agent steps are removed, which can lead to faster responses but reduce the accuracy. This is only supported for our new agent. 
* evaluate: whether to evaluate the generated SQL query.
* llm_config: is the configuration for the language model that will be used for NL generation. If you want to use open-source LLMs you should provide the api_base and llm_name. If you want to use OpenAI models don't specify api_base.
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
        "low_latency_mode": false,
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview"
        },
        "evaluate": false,
        "sql": "string",
        "metadata": {},
        "prompt": {
            "text": "string",
            "db_connection_id": "string",
            "schemas": [
                "string"
            ],
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
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview",
            "api_base": "string"
        },
        "intermediate_steps": [
            {
                "action": "string",
                "action_input": "string",
                "observation": "string"
            }
        ],
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
        "low_latency_mode": false,
        "llm_config": {
            "llm_name": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "api_base": "https://tt5h145hsc119q-8000.proxy.runpod.net/v1"
        },
        "evaluate": true,
        "metadata": {},
        "prompt": {
            "text": "What is the median rent in Miami?",
            "db_connection_id": "65baac8c35db7cdd1094be2e",
            "metadata": {}
        }
    }'


**Response example**

.. code-block:: rst

    {
        "id": "65bbb224142cc9bea23e2a08",
        "metadata": {},
        "created_at": "2024-02-01T15:00:52.005359+00:00",
        "prompt_id": "65bbb224142cc9bea23e2a07",
        "finetuning_id": null,
        "status": "VALID",
        "completed_at": "2024-02-01T15:01:22.540606+00:00",
        "llm_config": {
            "llm_name": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "api_base": "https://tt5h145hsc119q-8000.proxy.runpod.net/v1"
        },
        intermediate_steps": [
            {
            "thought": "I should Collect examples of Question/SQL pairs to check if there is a similar question among the examples.\n",
            "action": "FewshotExamplesRetriever",
            "action_input": "5",
            "observation": "samples ... "
            },
            ...
        ],
        "sql": "SELECT metric_value \nFROM renthub_median_rent \nWHERE period_type = 'monthly' \nAND geo_type = 'city' \nAND location_name = 'Miami' \nAND property_type = 'All Residential' \nAND period_end = (SELECT DATE_TRUNC('MONTH', CURRENT_DATE()) - INTERVAL '1 day')\nLIMIT 10",
        "tokens_used": 18115,
        "confidence_score": 0.95,
        "error": null
    }