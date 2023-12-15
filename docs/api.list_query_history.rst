List query history
=======================

After executing the **POST sync-schemas** endpoint, you will be able to access the `query_history` rows specific to each database
connection. This data can be utilized to generate new Golden records, albeit currently, this process must be carried out
manually through the **POST golden-records endpoint**.

Request this ``GET`` endpoint::

   /api/v1/query-history

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_connection_id", "string", "Database connection we want to get the logs, ``Required``"


**Responses**

HTTP 200 code response

.. code-block:: rst

    [
      {
        "id": "string",
        "db_connection_id": "string",
        "table_name": "string",
        "query": "string",
        "user": "string",
        "occurrences": "integer"
      }
    ]

**Request example**

.. code-block:: rst

    curl -X 'GET' \
      'http://localhost/api/v1/query-history?db_connection_id=656e52cb4d1fda50cae7b939' \
      -H 'accept: application/json'

**Response example**

.. code-block:: rst

    [
      {
        "id": "656e52da4d1fda50cae7b93a",
        "db_connection_id": "656e52cb4d1fda50cae7b939",
        "table_name": "foo",
        "query": "select QUERY_TEXT, USER_NAME, count(*) as occurrences from bar ...",
        "user": "user_name",
        "occurrences": 1
      }
    ]
