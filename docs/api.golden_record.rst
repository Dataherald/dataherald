Add golden records
=======================

Set golden records to improve the accuracy, so when a question is asked if there
is a golden record similar to the question it will be used as an example.

Request this ``POST`` endpoint::

   /api/v1/golden-record

**Request body**

.. code-block:: rst

   [
    {"nl_question": "question", "sql": "sql_query", "db":"db_alias"},
   ]

**Responses**

HTTP 200 code response

.. code-block:: rst

    True

**Example**


.. code-block:: rst

   curl -X 'POST' \
  '<host>/api/v1/golden-record' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
        {
            "nl_question":"what was the most expensive zip code to rent in Los Angeles county in May 2022?",
            "sql": "SELECT location_name, metric_value FROM table_name WHERE dh_county_name = '\''Los Angeles'\'' AND dh_state_name = '\''California'\''   AND period_start='\''2022-05-01'\'' AND geo_type='\''zip'\'' ORDER BY metric_value DESC LIMIT 1;",
            "db":"db_name"
        }
  ]'
