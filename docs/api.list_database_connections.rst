List Database connections
=============================

This endpoint list all the existing db connections

**Request this GET endpoint**::

   /api/v1/database-connections


**Responses**

HTTP 200 code response

.. code-block:: rst

    [
      {
        "id": "64dfa0e103f5134086f7090c",
        "alias": "databricks",
        "dialect": "databricks",
        "use_ssh": false,
        "connection_uri": "foooAABk91Q4wjoR2h07GR7_72BdQnxi8Rm6i_EjyS-mzz_o2c3RAWaEqnlUvkK5eGD5kUfE5xheyivl1Wfbk_EM7CgV4SvdLmOOt7FJV-3kG4zAbar=",
        "schemas": null,
        "path_to_credentials_file": null,
        "llm_api_key": null,
        "ssh_settings": null
      },
      {
        "id": "64e52c5f7d6dc4bc510d6d28",
        "alias": "postgres",
        "dialect": "postgres",
        "use_ssh": true,
        "connection_uri": null,
        "schemas": null,
        "path_to_credentials_file": "bar-LWxPdFcjQw9lU7CeK_2ELR3jGBq0G_uQ7E2rfPLk2RcFR4aDO9e2HmeAQtVpdvtrsQ_0zjsy9q7asdsadXExYJ0g==",
        "llm_api_key": "gAAAAABlCz5TeU0ym4hW3bf9u21dz7B9tlnttOGLRDt8gq2ykkblNvpp70ZjT9FeFcoyMv-Csvp3GNQfw66eYvQBrcBEPsLokkLO2Jc2DD-Q8Aw6g_8UahdOTxJdT4izA6MsiQrf7GGmYBGZqbqsjTdNmcq661wF9Q==",
        "ssh_settings": {
          "host": "string",
          "username": "string",
          "password": "foo-LWx6c1h6V0KkPRm9O148Pm9scvoO-wnasdasd1dQjf0ZQuFYI07uCjPiMcZ6uC19mUkiiYiHcKyok1NaLaGDAabkwg==",
          "private_key_password": "fooo-LWxPdFcjQw9lU7CeK_2ELR3jGBq0G_uQ7E2rfPLk2RcFR4aDO9e2HmeAQtVpdvtrsQ_0zjsy9q7asdsadXExYJ0g=="
        }
      }
    ]

**Example 1**

.. code-block:: rst

   curl -X 'GET' \
      '<host>/api/v1/database-connections' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json'
    '
