List questions
=======================

Once you have made a question you can use this endpoint to list these resources.

Request this ``GET`` endpoint::

   /api/v1/questions

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_connection_id", "string", "Database connection we want to get questions, ``Optional``"


**Responses**

HTTP 200 code response

.. code-block:: rst

    [
      {
        "id": "string",
        "question": "string",
        "db_connection_id": "string"
      }
    ]

**Request example**

.. code-block:: rst

   curl -X 'GET' \
  '<host>/api/v1/questions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json'

**Response example**

.. code-block:: rst

    [
      {
        "id": "64dfa0b603f5134086f7090b",
        "question": "what was the most expensive zip code to rent in Los Angeles county in May 2022?",
        "db_connection_id": "64dfa0e103f5134086f7090c"
      },
      {
        "id": "64dfa19603f5134086f7090e",
        "question": "what was the most expensive zip code to rent in Los Angeles county in May 2022?",
        "db_connection_id": "64dfa0e103f5134086f7090c"
      }
    ]
