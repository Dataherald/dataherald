Ask a question
=======================

Once you have set your db credentials, scanned the db, added table and columns description and added golden records
you should be able to ask natural language questions to retrieve an accurate response

Request this ``POST`` endpoint::

   /api/v1/questions

**Request body**

.. code-block:: rst

    {
      "db_connection_id": "string",
      "question": "string"
    }

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "run_evaluator", "boolean", "If True it evaluates the generated `sql_query` and `sql_query_result`, ``Optional``"
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
      "golden_record": false,
      "confidence_score": 0
    }

**Request example**

.. code-block:: rst

   curl -X 'POST' \
  '<host>/api/v1/questions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
      -d '{
      "question": "What is the median rent price for each property type in Los angeles city?",
      "db_connection_id": "651f2f542aa862650f3e737e"
    }'

**Response example**

.. code-block:: rst

   {
      "id": "64dbd8f4944f867b3c450468",
      "question_id": "64dbd8cf944f867b3c450467",
      "response": "The median rent price for single homes in Los Angeles city is approximately $2827.65.",
      "intermediate_steps": [
        "",
      ],
      "sql_query": "SELECT property_type, percentile_cont(0.5) WITHIN GROUP (ORDER BY metric_value) AS median_rent\nFROM db_table\nWHERE dh_city_name = 'Los Angeles'\nGROUP BY property_type\nLIMIT 13;",
      "sql_query_result": {
        "columns": [
          "property_type",
          "median_rent"
        ],
        "rows": [
          {
            "property_type": "single_homes",
            "median_rent": 2827.6479072398192
          }
        ]
      },
      "csv_file_path": null,
      "sql_generation_status": "VALID",
      "error_message": null,
      "exec_time": 37.183526277542114,
      "total_tokens": 17816,
      "total_cost": 1.1087399999999998,
      "golden_record": false,
      "confidence_score": 0.95
    }
