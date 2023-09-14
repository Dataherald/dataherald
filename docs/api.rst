API
=======================

The Dataherald Engine exposes RESTful APIs that can be used to:

* 🔌 Connect to and manage connections to databases
* 🔑 Add context to the engine through scanning the databases, adding descriptions to tables and columns and adding golden records
* 🙋‍♀️ Ask natural language questions from the relational data 

Our APIs have resource-oriented URL built around standard HTTP response codes and verbs. The core resources are described below.


Database Connections
------------------------------

The ``database-connections`` object allows you to define connections to your relational data stores. 

Related endpoints are:

* :doc:`Create database connection <api.create_database_connection>` -- ``POST api/v1/database-connections``
* :doc:`List database connections <api.list_database_connections>` -- ``GET api/v1/database-connections``
* :doc:`Update a database connection <api.update_database_connection>` -- ``PUT api/v1/database-connections/{alias}`` 


.. code-block:: json

    {
        "alias": "string",
        "use_ssh": false,
        "connection_uri": "string",
        "path_to_credentials_file": "string",
        "ssh_settings": {
            "db_name": "string",
            "host": "string",
            "username": "string",
            "password": "string",
            "remote_host": "string",
            "remote_db_name": "string",
            "remote_db_password": "string",
            "private_key_path": "string",
            "private_key_password": "string",
            "db_driver": "string"
        }
    }


Query Response
------------------
The ``query-response`` object is created from the answering natural language questions from the relational data.

The related endpoints are:

* :doc:`process_nl_query_response <api.process_nl_query_response>` -- ``POST api/v1/nl-query-responses``
* :doc:`update_nl_query_response <api.update_nl_query_response>` -- ``PATCH api/v1/nl-query-responses/{query_id}``


.. code-block:: json

    {
        "confidence_score": "string",
        "error_message": "string",
        "exec_time": "float",
        "intermediate_steps":["string"],
        "nl_question_id": "string",
        "nl_response": "string",
        "sql_generation_status": "string",
        "sql_query": "string",
        "sql_query_result": {},
        "total_cost": "float",
        "total_tokens": "int"
    }


Table Descriptions
---------------------
The ``table-descriptions`` object is used to add context about the tables and columns in the relational database.
These are then used to help the LLM build valid SQL to answer natural language questions.

Related endpoints are:

* :doc:`Scan table description <api.scan_table_description>` -- ``POST api/v1/table-descriptions/scan``
* :doc:`Add table description <api.add_descriptions>` -- ``PATCH api/v1/table-descriptions/{table_description_id}``
* :doc:`List table description <api.list_table_description>` -- ``GET api/v1/table-descriptions``

.. code-block:: json

    {
        "columns": [{}],
        "db_connection_id": "string",
        "description": "string",
        "examples": [{}],
        "table_name": "string",
        "table_schema": "string"
    }



.. toctree::
    :hidden:

    api.create_database_connection
    api.list_database_connections
    api.update_database_connection

    api.scan_table_description
    api.add_descriptions
    api.list_table_description

    api.golden_record

    api.question

    api.update_nl_query_response.rst
    api.process_nl_query_response
