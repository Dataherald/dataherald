Get a SQL Generation
============================

request this ``GET`` endpoint to get a SQL Generation.

    /api/v1/sql_generations/{sql_generation_id}

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "sql_generation_id", "string", "the id of a SQL query, ``Required``"


**Responses**

HTTP 200 code response

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

   curl -X 'GET' \
  'http://localhost/api/v1/sql-generations/65971ec8d274e27e2a360457' \
  -H 'accept: application/json'

**Response example**

.. code-block:: rst

    {
    "id": "65971ec8d274e27e2a360457",
    "metadata": null,
    "created_at": "2024-01-04 21:10:32.560000+00:00",
    "prompt_id": "65971ec8d274e27e2a360456",
    "finetuning_id": null,
    "status": "VALID",
    "completed_at": "2024-01-04 21:11:27.235000+00:00",
    "llm_config": {
      "llm_name": "gpt-4-turbo-preview",
      "api_base": null
    },
    "intermediate_steps": [
      {
        "thought": "I should Collect examples of Question/SQL pairs to check if there is a similar question among the examples.\n",
        "action": "FewshotExamplesRetriever",
        "action_input": "5",
        "observation": "Found 5 examples of similar questions."
        },
        ...
    ],
    "sql": "\nSELECT dh_zip_code, MAX(metric_value) as highest_rent -- Select the zip code and the maximum rent value\nFROM renthub_average_rent\nWHERE dh_county_name = 'Los Angeles' -- Filter for Los Angeles county\nAND period_start <= '2022-05-01' -- Filter for the period that starts on or before May 1st, 2022\nAND period_end >= '2022-05-31' -- Filter for the period that ends on or after May 31st, 2022\nGROUP BY dh_zip_code -- Group by zip code to aggregate rent values\nORDER BY highest_rent DESC -- Order by the highest rent in descending order\nLIMIT 1; -- Limit to the top result\n",
    "tokens_used": 12185,
    "confidence_score": null,
    "error": null
    }