Execute a SQL generation
==========================

This endpoint can be used to execute a SQL query and get the results in a json format.

Request this ``GET`` endpoint to execute a SQL query and get the results in a json format::

    api/v1/sql-generations/{sql_generation_id}/execute


**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "sql_generation_id", "string", "The id of the SQL query you want to execute, ``Optional``"
   "max_rows", "integer", "the maximum number of rows to return, ``Optional``"

**Responses**

HTTP 201 code response

.. code-block:: rst

    [
        "string",
        {
            "result": [
                {
                }]
        }
    ]

**Request example**

.. code-block:: rst

    curl -X 'GET' \
    'http://localhost/api/v1/sql-generations/65971ec8d274e27e2a360457/execute?max_rows=5' \
    -H 'accept: application/json'



**Response example**

.. code-block:: rst

    [
        "[('91302', 13219.153846153846)]",
        {
            "result": [
            {
                "dh_zip_code": "91302",
                "highest_rent": 13219.153846153846
            }
            ]
        }
    ]