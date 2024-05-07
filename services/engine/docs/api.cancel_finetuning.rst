Cancel a finetuning job
========================

This endpoint allows you to cancel a finetuning job, which will stop the training process but will not delete the job from the collection of finetuning jobs.

request this ``POST`` endpoint to cancel a finetuning job.

    /api/v1/finetunings/<finetuning_id>/cancel

**Request body**

.. code-block:: rst

    {
        "finetuning_id": "finetuing-job-id",
        "metadata": dict[str, str] | None
    }

**Responses**

HTTP 200 code response

.. code-block:: rst

    {
        "id": "finetuing-job-id",
        "db_connection_id": "database_connection_id"
        "alias": "model name"
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
    'http://localhost/api/v1/finetunings/{finetuning_id}/cancel' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "finetuning_id": "finetuning-job-id"
    }'


**Response example**

.. code-block:: rst

    {
    "id": "finetuning-job-id",
    "alias": "my_model",
    "db_connection_id": "database_connection_id",
    "status": "cancelled",
    "error": "Fine tuning cancelled by the user",
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

