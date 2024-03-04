Error Codes
=============================

When encountering errors in the API, an error code and a brief explanation are provided,
along with a 400 HTTP status code, following this structure:

.. code-block:: rst

    {
        "error_code": "<error_code>",
        "message": <error_message>,
        "description": <description>,
        "detail": {
            <body_params>
        }
    }

**Error Codes:**

DB Connections

- `invalid_database_connection` - Unable to establish the database connection.
- `invalid_database_uri_format` - The `connection_uri` doesn't have the correct format.
- `ssh_invalid_database_connection` - The SSH connection failed.
- `empty_database` - Although the connection was established, there are no tables present.
- `database_connection_not_found` - Database resource could not be found.

Golden SQL

- `golden_sql_not_found` - Golden SQL resource not found.
- `invalid_golden_sql` - The Golden SQL doesn't have the correct format.

Finetuning Model

- `llm_model_not_supported` - The specified model is not supported.

SQL Generation

- `prompt_not_found` - Prompt resource not found.
- `sql_generation_not_created` - The SQL generation failed.
- `sql_injection` - The generated/provided SQL failed the injection validation.
- `sql_generation_not_found` - SQL generation resource not found.

NL Generation

- `nl_generation_not_created` - The NL generation failed.

**Other Errors**

- `invalid_object_id` - The provided string is not a valid ObjectId.
