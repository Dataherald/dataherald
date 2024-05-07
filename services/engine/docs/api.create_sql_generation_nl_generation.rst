Create a prompt, a SQL query and NL response
============================================

This endpoint can be used to create a prompt, a SQL query and NL response at the same time. The prompt is used to generate the SQL query and the SQL query is used to generate the NL response.
This endpoint has all of the parameters required for prompts, SQL generation, and NL generation.

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
* llm_config: is the configuration for the language model that will be used for NL generation. If you want to use open-source LLMs you should provide the api_base and llm_name. If you want to use OpenAI models don't specify api_base.
* evaluate: whether to evaluate the generated SQL query.
* sql: if you want to manually create the SQL query you can provide it here. If this is not provided we use the prompt to generate the SQL query.


Request this ``POST`` endpoint to create a SQL query, a NL response, and a given prompt::

    api/v1/prompts/{prompt_id}/sql-generations/nl-generations

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "prompt_id", "string", "the Prompt id which you want to create SQL and NL answer., ``Required``"

**Request body**

.. code-block:: rst

   {
        "max_rows": 100,
        "llm_config": {
            "llm_name": "string",
            "api_base": "string"
        },
        "metadata": {},
        "sql_generation": {
            "finetuning_id": "string",
            "low_latency_mode": flase,
            "llm_config": {
                "llm_name": "string",
                "api_base": "string"
            },
            "evaluate": false,
            "sql": "string",
            "metadata": {},
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
            "llm_name": "string",
            "api_base": "string"
        },
        "sql_generation_id": "string",
        "text": "string"
    }

**Request example**

.. code-block:: rst

    curl -X 'POST' \
        'http://localhost/api/v1/prompts/65bbb224142cc9bea23e2a07/sql-generations/nl-generations' \
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
            "metadata": {}
        }
    }'


**Response example**

.. code-block:: rst

    {
        "id": "65bbb307142cc9bea23e2a0a",
        "metadata": {},
        "created_at": "2024-02-01T15:04:39.808060+00:00",
        "llm_config": {
            "llm_name": "gpt-4-turbo-preview",
            "api_base": null
        },
        "sql_generation_id": "65bbb2c7142cc9bea23e2a09",
        "text": "The median rent in Miami is $3,131.0."
    }