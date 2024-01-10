.. _api.list_finetunings:

List Finetunings
===========================

You can use this endpoint to retrieve a list of finetunings for a given database connection.

Request this ``GET`` endpoint::

    GET /api/v1/finetunings

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_connection_id", "string", "Database connection we want to get finetunings, ``Optional``"

**Responses**

HTTP 201 code response

.. code-block:: rst

    [
        {
            "id": "finetuning-job-id",
            "db_connection_id": "database_connection_id",
            "alias": "my_model",
            "status": "validating_files",
            "error": null,
            "base_llm": {
                "model_provider": "openai",
                "model_name": "gpt-3.5-turbo-1106",
                "model_parameters": {
                "n_epochs": "1"
                }
            },
            "finetuning_file_id": null,
            "finetuning_job_id": null,
            "model_id": null,
            "created_at": "2023-12-13T17:35:53.263485",
            "golden_records": [ # a list of golden record ids, keep in mind that at least 10 golden records are required for openai models finetuning
                "656777c9eb4e22533dc43fce",
                "656777ceeb4e22533dc43fcf",
                "656777ceeb4e22533dc43fd0",
                "656777ceeb4e22533dc43fd1",
                "656777ceeb4e22533dc43fd2",
                "656777ceeb4e22533dc43fd3",
                "656777ceeb4e22533dc43fd4",
                "656777ceeb4e22533dc43fd5",
                "656777ceeb4e22533dc43fd6",
                "656777ceeb4e22533dc43fd7",
                "656777ceeb4e22533dc43fd8",
                "656777ceeb4e22533dc43fd9",
                "656777ceeb4e22533dc43fda",
                "656777ceeb4e22533dc43fdb",
                "656777ceeb4e22533dc43fdc",
                "656777ceeb4e22533dc43fdd",
                "656777ceeb4e22533dc43fde",
            ],
            "metadata": null
        }
    ]

**Example**

.. code-block:: rst

   curl -X 'GET' \
  '<host>/api/v1/finetunings?db_connection_id=12312312' \
  -H 'accept: application/json
