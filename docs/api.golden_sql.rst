.. _api.golden_record:

Golden Records
=======================

In order to improve the perfromance of NL-to-SQL engines, our system includes a few verfied Question SQL samples in the prompts.
As more samples are verfied, the performance of the NL-to-SQL engine not only improves in terms of accuracy but also improves in terms speed.
The verfied Question SQL samples are called golden records. These golden records are stored in vector database for fast retrieval and also in our application storage for easy access and management.


Add golden records
-------------------

You can add golden records to the system by sending a POST request to the ``/api/v1/golden-record`` endpoint.

Request this ``POST`` endpoint::

   /api/v1/golden-records

**Request body**

.. code-block:: rst

   [
    {"question": "question", "sql_query": "sql_query", "db_connection_id":"db_connection_id"},
   ]

**Responses**

HTTP 201 code response

.. code-block:: rst

   [
    {"id": "id", "question": "question", "sql_query":"sql", db_connection_id: "db_connection_id"},
   ]

**Example**


.. code-block:: rst

   curl -X 'POST' \
  'http://localhost/api/v1/golden-records' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "question": "what was the median home sale price in Califronia in Q1 2021?",
    "sql_query": "SELECT location_name, period_end, metric_value FROM redfin_median_sale_price rmsp WHERE geo_type = '\''state'\'' AND location_name='\''California'\'' AND property_type = '\''All Residential'\''   AND period_start BETWEEN '\''2021-01-01'\'' AND '\''2021-03-31'\'' ORDER BY period_end;",
    "db_connection_id": "64dfa0e103f5134086f7090c",
  }]'

Delete golden records
-----------------------

You can delete a golden record by sending a DELETE request to the ``/api/v1/golden-record/{golden_record_id}`` endpoint.

Request this ``DELETE`` endpoint::

   /api/v1/golden-records/{golden_record_id}

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 15, 10, 30

   "golden_record_id", "string", "Generated golden record id, ``Required``"

**Responses**

HTTP 200 code response

.. code-block:: rst

    {"status": true}

**Example**

.. code-block:: rst

   curl -X 'DELETE' \
  'http://localhost/api/v1/golden-records/64e503fa85dbfee0d981f8ce' \
  -H 'accept: application/json'


Get golden records
-----------------------


Request this ``GET`` endpoint::

   /api/v1/golden-records

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 15, 10, 30

   "db_connection_id", "string", "db connection id, ``Optoinal``"
   "page", "integer", "Page number, ``Optoinal``"
   "limit", "integer", "Page size, ``Optoinal``"

**Responses**

HTTP 200 code response

.. code-block:: rst

   [
   {"id": "id", "question": "question", "sql_query":"sql", db_connection_id: "db_connection_id"},
   ]

**Example**

.. code-block:: rst

   curl -X 'GET' \
  'http://localhost/api/v1/golden-records?page=1&limit=10&db_connection_id=2342344' \
  -H 'accept: application/json'
