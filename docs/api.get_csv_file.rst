Export a CSV file
=========================

This endpoint can be used to export a csv file for a given SQL query.

Request this ``GET`` endpoint to execute a SQL query and get the results in a csv format::

    api/v1/sql-generations/{sql_generation_id}/csv-file


**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "sql_generation_id", "string", "The id of the SQL query you want to execute, ``Optional``"

**Request example**

.. code-block:: rst

    curl -X 'GET' \
    'http://localhost/api/v1/sql-generations/65971ec8d274e27e2a360457/csv-file' \
    -H 'accept: application/json'