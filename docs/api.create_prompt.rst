Create a Prompt
=============================

Prompts are the resource that contains the text that is going to be passed to large language models.

Prompts are passed to the agents for SQL generation and each prompt can have one or more SQL generations associated with it that are from different models and agents.


Request this ``POST`` endpoint to create a finetuning job::

    /api/v1/prompts

**Request body**

.. code-block:: rst

   {
        "text": "string",
        "db_connection_id": "string",
        "schemas": [
            "string"
        ],
        "metadata": {}
    }

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
        "id": "string",
        "metadata": {},
        "created_at": "string",
        "text": "string",
        "db_connection_id": "string",
        "schemas": [
            "string"
        ]
    }

**Request example**

.. code-block:: rst

    curl -X 'POST' \
    'http://localhost/api/v1/finetunings' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "text": "your question or command here",
    "db_connection_id": "database_connection_id"
    }'


**Response example**

.. code-block:: rst

    {
        "id": "db_connection_id",
        "metadata": {},
        "created_at": "2024-01-10 20:35:27.106717",
        "text": "What is the average salary of employees in the company?",
        "db_connection_id": "db_connection_id"
    }