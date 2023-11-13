Create a new response
=============================

After utilizing the `questions` endpoint, you have the option to generate a new `response`
associated with a specific `question_id`. You can modify the `sql_query` to produce an alternative
`sql_query_result` and a distinct response. In the event that you do not specify a `sql_query`,
the system will reprocess the question to generate the `sql_query`, execute the `sql_query_result`,
and subsequently generate the response.

Request this ``POST`` endpoint::

   /api/v1/responses

**Request body**

.. code-block:: rst

    {
      "question_id": "string", # required
      "sql_query": "string" # optional
    }

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "run_evaluator", "boolean", "If True it evaluates the generated `sql_query` and `sql_query_result`, ``Optional``"
   "sql_response_only", "boolean", "If True it only runs the SQL and returns the `sql_query_result`, ``Optional``"
   "generate_csv", "boolean", "If True it responses `sql_result` as NULL if it has more than 50 rows and generates the CSV file, ``Optional``"

If the generate_csv flag is set to True, and the sql_query_result contains more than 50 rows, the system will utilize either
the S3 credentials specified in the environment variables or those configured within the db_connection to generate the CSV file.
The resulting file path will be structured as follows:

.. code-block:: rst

    "csv_file_path": "s3://k2-core/c6ddccfc-f355-4477-a2e7-e43f77e31bbb.csv"

**Responses**

HTTP 201 code response

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
      "csv_file_path": "string",
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
      "question_id": "64dbd8cf944f867b3c450467"
    }'

**Response example**

.. code-block:: rst

   {
      "id": "64c424fa3f4036441e882352",
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
      "csv_file_path": null,
      "sql_generation_status": "VALID",
      "error_message": null,
      "exec_time": 37.183526277542114,
      "total_tokens": 17816,
      "total_cost": 1.1087399999999998
      "confidence_score": 0.95
    }
