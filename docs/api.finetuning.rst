Create a finetuning job
=========================

One of the features that our framework provides is the ability to finetune a model on your golden records. This model is going to be used inside an Agent for generating SQL queries for the given input. The finetuning job is going to be created asynchronously and you can check the status of the job by using the GET /api/v1/finetuning-jobs/<finetuning_id> endpoint.

This endpoint will create a file that is expected to be uploaded to the model provider. After the file is uploaded, we will create a finetuning job and train the model. After the model is trained, the model provider will assign a model id to the model and you can use this model id inside our agent.

The only required parameter for this endpoint is the ``db_connection_id``. This is the id of the database connection that you want to use for finetuning. You can get the list of database connections by using the GET /api/v1/db-connections endpoint.


Request this ``POST`` endpoint to create a finetuning job::

    /api/v1/finetunings

**Request body**

.. code-block:: rst

   {
        "db_connection_id": "database_connection_id"
        "alias": "model name",
        "base_llm": {
            "model_provider": "model_provider_name" # right now openai is the only provider.
            "model_name": "model_name" # right now gpt-3.5-turbo and gpt-4 are suported.
            "model_parameters": {
                "n_epochs": int or string, #optional, default value 3
                "batch_size": int or string, #optional, default value 1
                "learning_rate_multiplier", int or string, #optional, default value "auto"
            }
        }
        "golden_records": array[ids] #optional, default value is none which means use all of the golden records
        "metadata": dict[str, str] | None} #optional, default value None
    }

**Responses**

HTTP 201 code response

.. code-block:: rst

    {
        "id": "finetuing-job-id",
        "db_connection_id": "database_connection_id",
        "alias": "model name",
        "status": "finetuning_job_status" # queued is default other possible values are [queued, running, succeeded, failed, validating_files, or cancelled]
        "error": "The error message if the job failed" # optional default value is None
        "base_llm": {
            "model_provider": "model_provider_name" # right now openai is the only provider.
            "model_name": "model_name" # right now gpt-3.5-turbo and gpt-4 are suported.
            "model_parameters": {
                "n_epochs": int or string, #optional, default value 3
                "batch_size": int or string, #optional, default value 1
                "learning_rate_multiplier", int or string, #optional, default value "auto"
            }
        }
        "finetuning_file_id": "This is the file id that is assigned by model provider when uploading the finetuning file"
        "finetuning_job_id": "The is the finetuning job id that is assigned by model provider when creating the finetuning job"
        "model_id": "The is the model id that is assigned by model provider after finetuning job is done"
        "created_at": datetime,
        "golden_records": array[ids], # default value is none which means use all of the golden records
        "metadata": dict[str, str] | None} #optional, default value None
    }

**Request example**

.. code-block:: rst

    curl -X 'POST' \
    'http://localhost/api/v1/finetunings' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "db_connection_id": "database_connection_id",
    "alias": "my_model",
    "base_llm": {
        "model_provider": "openai",
        "model_name": "gpt-3.5-turbo-1106",
        "model_parameters": {
        "n_epochs": 1
        }
    }
    }'


**Response example**

.. code-block:: rst

    {
    "id": "finetuning-job-id",
    "alias": "my_model",
    "db_connection_id": "database_connection_id",
    "status": "queued",
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
        "656777ceeb4e22533dc43fde"
    ],
    "metadata": null
    }
