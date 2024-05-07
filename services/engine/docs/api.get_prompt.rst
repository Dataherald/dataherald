Get a prompt
============================

request this ``GET`` endpoint to get a prompt.

    /api/v1/prompts/<prommpt_id>

**Responses**

HTTP 200 code response

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

   curl -X 'GET' \
  'http://localhost/api/v1/prompts/65957febfef5f74dddsf643434' \
   -H 'accept: application/json'

**Response example**

.. code-block:: rst

    {
    "id": "65957febfef5f74sdfsd0693434",
    "metadata": null,
    "created_at": "2024-01-03 15:40:27.624000+00:00",
    "text": "What is the expected total full year sales in 2023?",
    "db_connection_id": "659435a5453d359345834"
    "schemas": [
        "public"
    ]
    }