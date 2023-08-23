.. _api.golden_record:

golden records
=======================

In order to improve the perfromance of NL-to-SQL engines, our system includes a few verfied Question SQL samples in the prompts.
As more samples are verfied, the performance of the NL-to-SQL engine not only improves in terms of accuracy but also improves in terms speed.
The verfied Question SQL samples are called golden records. These golden records are stored in vector database for fast retrieval and also in our application storage for easy access and management.


Add golden records
-------------------

You can add golden records to the system by sending a POST request to the ``/api/v1/golden-records/{namespace}`` endpoint.

Request this ``POST`` endpoint::

   /api/v1/golden-records/{namespace}


**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 15, 10, 30

   "namespace", "string", "namespace, ``Required``"

**Request body**

.. code-block:: rst

   [
    {"nl_question": "question", "sql": "sql_query", "db":"db_alias"},
   ]

**Responses**

HTTP 200 code response

.. code-block:: rst

   [
    {"nl_question": "question", "sql": "sql_query", "db":"db_alias"},
   ]

**Example**


.. code-block:: rst

   curl -X 'POST' \
  'http://localhost/api/v1/golden-records/dataherald' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "nl_question": "what was the most expensive zip code to rent in Los Angeles county in May 2022?",
    "sql": "SELECT location_name, metric_value FROM renthub_median_rent WHERE dh_county_name = '\''Los Angeles'\'' AND dh_state_name = '\''California'\'' AND property_type = '\''All Residential'\'' AND period_start='\''2022-05-01'\'' AND geo_type='\''zip'\'' ORDER BY metric_value DESC LIMIT 1;",
    "db": "v2_real_estate"
  }]'

Delete golden records
-----------------------

You can delete a golden record by sending a DELETE request to the ``/api/v1/golden-records/{namespace}/{golden_record_id}`` endpoint.

Request this ``DELETE`` endpoint::

   /api/v1/golden-records/{namespace}/{golden_record_id}

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 15, 10, 30

   "namespace", "string", "namespace, ``Required``"
   "golden_record_id", "string", "Generated golden record id, ``Required``"

**Responses**

HTTP 200 code response

.. code-block:: rst

    {"status": true}

**Example**

.. code-block:: rst

   curl -X 'DELETE' \
  'http://localhost/api/v1/golden-records/dataherald/64e60cecdb56b85392a41bc7/' \
  -H 'accept: application/json'


Get golden records
-----------------------

You can get golden record with pagination by sending a GET request to the ``/api/v1/golden-records/{namespace}`` endpoint.

Request this ``GET`` endpoint::

   /api/v1/golden-records/{namespace}

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 15, 10, 30

   "namespace", "string", "namespace, ``Required``"
   "page", "integer", "Page number, ``Optoinal``"
   "limit", "integer", "Page size, ``Optoinal``"

**Responses**

HTTP 200 code response

.. code-block:: rst

   [
    {"id": "id", "question": "question", "sql_query":"sql", db_alias: "database alias", "namespace":"namespace", "created_time": "created_time"},
   ]

**Example**

.. code-block:: rst

   curl -X 'GET' \
  'http://localhost/api/v1/golden-records/dataherald?page=1&limit=10' \
  -H 'accept: application/json'
