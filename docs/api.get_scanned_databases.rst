Get a scanned database
=============================

Once a database was scanned you can use this endpoint to retrieve the
tables names and columns

Request this ``GET`` endpoint::

   /api/v1/scanned-databases

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "db_alias", "string", "DB alias, ``Required``"

**Responses**

HTTP 200 code response

.. code-block:: rst

    {
      "db_alias": "string",
      "tables": [
        {
          "id": "string",
          "name": "string",
          "columns": [
            "string"
          ]
        }
      ]
    }

**Request example**

.. code-block:: rst

   curl -X 'GET' \
  '<host>/api/v1/scanned-databases?db_alias=databricks' \
  -H 'accept: application/json'

**Response example**

.. code-block:: rst

    {
      "db_alias": "databricks",
      "tables": [
        {
          "id": "64dfa18c03f5134086f7090d",
          "name": "median_rent",
          "columns": [
            "period_start",
            "period_end",
            "period_type",
            "geo_type",
            "property_type",
            "location_name",
            "metric_value"
          ]
        }
      ]
    }
