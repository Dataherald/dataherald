List SQL generations
============================

request this ``GET`` endpoint to get a list of all SQL generations

    /api/v1/sql_generations


**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "prompt_id", "string", "the prompt id, ``Optional``"


**Responses**

HTTP 200 code response

.. code-block:: rst

    [
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
    ]

**Request example**

.. code-block:: rst

   curl -X 'GET' \
  'http://localhost/api/v1/sql-generations?prompt_id=6595ad38fef5f74dd00695a3' \
  -H 'accept: application/json'

**Response example**

.. code-block:: rst

    [
        {
            "id": "6595ad38fef5f74dd00695a4",
            "metadata": null,
            "created_at": "2024-01-03 18:53:44.376000+00:00",
            "prompt_id": "6595ad38fef5f74dd00695a3",
            "finetuning_id": null,
            "status": "VALID",
            "completed_at": "2024-01-03 18:54:55.091000+00:00",
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
            "sql": "\nSELECT metric_value -- Rent price\nFROM renthub_median_rent\nWHERE geo_type='city' -- Focusing on city-level data\n  AND dh_state_name = 'California' -- State is California\n  AND dh_place_name = 'Los Angeles' -- City is Los Angeles\n  AND period_start = '2023-06-01' -- Most recent data available\nORDER BY metric_value DESC -- In case there are multiple entries, order by price descending\nLIMIT 1; -- Only need the top result\n",
            "tokens_used": 9491,
            "confidence_score": null,
            "error": null
        }
    ]