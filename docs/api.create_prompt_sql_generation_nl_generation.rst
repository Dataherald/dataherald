Create a SQL query and NL response
===================================

This endpoint can be used to create a SQL query and NL response for a given prompt.
This endpoint has all of the parameters required for SQL generation and NL generation.

NL generation parameters
------------------------

The following parameters are used for NL generation:

* max_rows: the maximum number of rows to return in the NL response
* llm_config: is the configuration for the language model that will be used for NL generation. If you want to use open-source LLMs you should provide the api_base and llm_name. If you want to use OpenAI models don't specify api_base.

SQL generation parameters
-------------------------

The following parameters are used for SQL generation:

* finetuning_id: the id of the finetuning model. If this is not provided we use a reasoning LLM with retrieval augmented generation. If specified we use the finetuning model for sql generation.
* low_latency_mode: When this flag is set, some of the agent steps are removed, which can lead to faster responses but reduce the accuracy. This is only supported for our new agent. 
* evaluate: whether to evaluate the generated SQL query.
* llm_config: is the configuration for the language model that will be used for NL generation. If you want to use open-source LLMs you should provide the api_base and llm_name. If you want to use OpenAI models don't specify api_base.
* sql: if you want to manually create the SQL query you can provide it here. If this is not provided we use the prompt to generate the SQL query.



Request this ``POST`` endpoint to create a SQL query and a NL response for a given prompt::

    api/v1/prompts/{prompt_id}/sql-generations/nl-generations

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "prompt_id", "string", "the prompt id that we want to create a SQL query and NL response for, ``Required``"


**Request body**

.. code-block:: rst

   {
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview",
            "api_base": "string"
        },
        "max_rows": 100,
        "metadata": {},
        "sql_generation": {
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
    }

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
        "id": "string",
        "metadata": {},
        "created_at": "string",
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview",
            "api_base": "string"
        },
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
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview"
        },
        "max_rows": 100,
        "metadata": {},
        "sql_generation": {
            "low_latency_mode": false,
            "llm_config": {
            "llm_name": "gpt-4-turbo-preview"
            },
            "evaluate": false,
            "metadata": {},
            "prompt": {
            "text": "What is the average rent price in LA?",
            "db_connection_id": "65baac8c35db7cdd1094be2e",
            "metadata": {}
            }
        }
    }'


**Response example**

.. code-block:: rst

    {
        "id": "65bbb104142cc9bea23e2a03",
        "metadata": {},
        "created_at": "2024-02-01T14:56:04.884063+00:00",
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview",
            "api_base": null
        },
        "sql_generation_id": "65bbb09a142cc9bea23e2a02",
        "text": "The average rent price in LA is approximately $2,757.48."
    }