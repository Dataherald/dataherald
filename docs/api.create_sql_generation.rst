Create a SQL query
============================================

This endpoint can be used to create a SQL query for a given prompt.

SQL generation parameters
-------------------------

The following parameters are used for SQL generation:

* finetuning_id: the id of the finetuning model. If this is not provided we use a reasoning LLM with retrieval augmented generation. If specified we use the finetuning model for sql generation.
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
        "sql": "string",
        "tokens_used": 0,
        "confidence_score": 0,
        "error": "string"
    }

**Request example**

.. code-block:: rst

    curl -X 'POST' \
    'http://localhost/api/v1/prompts/659823133d20c828021c9516/sql-generations' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "evaluate": false
    }'


**Response example**

.. code-block:: rst

    {
        "id": "659ffed5fb38253f83458070",
        "metadata": null,
        "created_at": "2024-01-11 14:44:37.629631",
        "prompt_id": "659823133d20c828021c9516",
        "finetuning_id": null,
        "status": "VALID",
        "completed_at": "2024-01-11 14:45:51.220709",
        "sql": "-- Select the average rent price for 'Los Angeles' city in 'California'\nSELECT \n    dh_state_name, -- Include the state name as per admin instructions\n    AVG(metric_value) AS average_rent_price -- Calculate the average rent price\nFROM \n    renthub_average_rent\nWHERE \n    geo_type = 'city' -- Filter by city geo_type\n    AND location_name = 'Los Angeles' -- Filter by 'Los Angeles' location\n    AND dh_state_name = 'California' -- Filter by 'California' state\n    AND property_type = 'All Residential' -- Filter by 'All Residential' property type as per admin instructions\n    AND period_end = '2023-12-31' -- Filter by the last date of the most recent complete month\nGROUP BY \n    dh_state_name -- Group by state name to include it in the select",
        "tokens_used": 14211,
        "confidence_score": null,
        "error": null
    }