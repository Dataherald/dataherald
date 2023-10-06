Process a NL query response
=============================

Once you made a question you can try sending a new sql query to improve the response, this is not stored

Request this ``POST`` endpoint::

   /api/v1/responses

**Request body**

.. code-block:: rst

    {
      "query_id": "string", # required
      "sql_query": "string" # required
    }

**Responses**

HTTP 200 code response

.. code-block:: rst

    {
      "id": "string",
      "question_id": "string",
      "response": "string",
      "intermediate_steps": [
        "string"
      ],
      "sql_query": "string",
      "sql_query_result": {
        "columns": [
          "string"
        ],
        "rows": [
          {}
        ]
      },
      "sql_generation_status": "NONE",
      "error_message": "string",
      "exec_time": 0,
      "total_tokens": 0,
      "total_cost": 0,
      "confidence_score": 0
    }

**Request example**


.. code-block:: rst

   curl -X 'POST' \
  '<localhost>/api/v1/responses' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
      "sql_query": "SELECT "dh_zip_code", MAX("metric_value") as max_rent
        FROM db_table
        WHERE "dh_county_name" = 'Los Angeles' AND "period_start" = '2022-05-01' AND "period_end" = '2022-05-31'
        GROUP BY "zip_code"
        ORDER BY max_rent DESC
        LIMIT 1;",
      "query_id": "64c424fa3f4036441e882352"
    }'

**Response example**

.. code-block:: rst

   {
      "id": {
        "$oid": "64c424fa3f4036441e882352"
      },
      "question_id": "64dbd8cf944f867b3c450467",
      "response": "The most expensive zip to rent in Los Angeles city is 90210",
      "intermediate_steps": [
        "",
      ],
      "sql_query": "SELECT "zip_code", MAX("metric_value") as max_rent
        FROM db_table
        WHERE "dh_county_name" = 'Los Angeles' AND "period_start" = '2022-05-01' AND "period_end" = '2022-05-31'
        GROUP BY "zip_code"
        ORDER BY max_rent DESC
        LIMIT 1;",
      "sql_query_result": {
        "columns": [
          "zip_code",
          "max_rent"
        ],
        "rows": [
          {
            "zip_code": "90210",
            "max_rent": 58279.6479072398192
          }
        ]
      },
      "sql_generation_status": "VALID",
      "error_message": null,
      "exec_time": 37.183526277542114,
      "total_tokens": 17816,
      "total_cost": 1.1087399999999998
      "confidence_score": 0.95
    }
