Create a SQL query and NL response
===================================

This endpoint can be used to create a SQL query and NL response for a given prompt.
This endpoint has all of the parameters required for SQL generation and NL generation.

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
        "max_rows": 100,
        "metadata": {},
        "sql_generation": {
            "finetuning_id": "string",
            "evaluate": false,
            "sql": "string",
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
        "sql_generation_id": "string",
        "text": "string"
    }

**Request example**

.. code-block:: rst

    curl -X 'POST' \
        'http://localhost/api/v1/prompts/6598246b55b78760ff3f205c/sql-generations/nl-generations' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "max_rows": 100,
        "metadata": {},
        "sql_generation": {
            "evaluate": false,
            "metadata": {}
        }
    }'


**Response example**

.. code-block:: rst

    {
    "id": "659f141ffb38253f83458067",
    "metadata": {},
    "created_at": "2024-01-10 22:03:11.422172",
    "sql_generation_id": "659f1396fb38253f83458066",
    "text": "The average rent price in Los Angeles, California, as of the most recent data on November 30, 2023, is $3,367.66."
    }