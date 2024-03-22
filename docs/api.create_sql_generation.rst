Create a SQL query
============================================

This endpoint can be used to create a SQL query for a given prompt.

SQL generation parameters
-------------------------

The following parameters are used for SQL generation:

* finetuning_id: the id of the finetuning model. If this is not provided we use a reasoning LLM with retrieval augmented generation. If specified we use the finetuning model for sql generation.
* low_latency_mode: When this flag is set, some of the agent steps are removed, which can lead to faster responses but reduce the accuracy. This is only supported for our new agent. 
* evaluate: whether to evaluate the generated SQL query.
* sql: if you want to manually create the SQL query you can provide it here. If this is not provided we use the prompt to generate the SQL query.


Request this ``POST`` endpoint to create a SQL query for a given prompt::

    api/v1/prompts/{prompt_id}/sql-generations


**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "prompt_id", "string", "the prompt id of the prompt that you want to generate a SQL query for, ``Required``"


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
        "metadata": {}
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
    'http://localhost/api/v1/prompts/65bbb224142cc9bea23e2a07/sql-generations' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "low_latency_mode": false,
    "llm_config": {
        "llm_name": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "api_base": "https://tt5h145hsc119q-8000.proxy.runpod.net/v1"
    },
    "evaluate": false,
    "metadata": {}
    }'


**Response example**

.. code-block:: rst

    {
    "id": "65bbb400142cc9bea23e2a0c",
    "metadata": {},
    "created_at": "2024-02-01T15:08:48.370228+00:00",
    "prompt_id": "65bbb224142cc9bea23e2a07",
    "finetuning_id": null,
    "status": "VALID",
    "completed_at": "2024-02-01T15:09:10.474942+00:00",
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
    "confidence_score": null,
    "error": null
    }