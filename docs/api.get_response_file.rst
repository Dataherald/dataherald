Get a response file
=============================

After configuring your S3 credentials either through environment variables or within the db_connection endpoint, and
enabling the generate_csv flag when making ``POST`` requests to ``/questions`` or ``/responses`` endpoints, once a file has been
generated, you can utilize this endpoint to get the CSV file content.

Request this ``GET`` endpoint::

   /api/v1/responses/{response_id}/file

**Parameters**

.. csv-table::
   :header: "Name", "Type", "Description"
   :widths: 20, 20, 60

   "response_id", "string", "The response id, ``Required``"


**Responses**

HTTP 200 code response

.. code-block:: rst
    The file content

**Request example**

.. code-block:: rst

   curl -X 'GET' \
  '<localhost>/api/v1/responses/64c424fa3f4036441e882352/file' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json'

**Response example**

.. code-block:: rst

    customer,sales
    Foo,12.0
    Bar,39
    ...
