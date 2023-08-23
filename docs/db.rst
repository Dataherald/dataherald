Application Storage (DB)
=========================

The application storage (referred to as DB in the code) is the database that stores the Dataherald AI application logic. The engine currently only includes MongoDB as a supported Application Storage implementation.


Stored Information
-------------------

The application logic is stored in the following Mongo collections:

1. ``database_connection``- Stores the information needed to connect to a structured database to be queried.
2. ``nl_question`` - List of natural language questions asked so far through the ``/question`` endpoint
3. ``nl_query_response`` - Stores generated responses from Dataherald AI engine, including 
4. ``table_schema_detail`` - Stores metadata about the tables and columns from the connected structured data stores. These can be added automatically from a scan or manually by the admin.

Abstract Storage Class
----------------------

All implementations of the Application Storage module must inherit and implement the abstract `DB` class. While MongoDB is the only supported implementation at this time, the abstract class is designed to be easily extended to support other storage solutions.


:class:`DB`
^^^^^^^^^^^^

This abstract class provides a consistent interface for working with different storage solutions.

.. method:: insert_one(self, collection: str, obj: dict) -> int

   Inserts a single document into the specified collection.

.. method:: update_or_create(self, collection: str, query: dict, obj: dict) -> int

   Updates or creates a document in the specified collection based on a query.

.. method:: find_one(self, collection: str, query: dict) -> dict

   Retrieves a single document from the specified collection based on a query.

.. method:: find_by_id(self, collection: str, id: str) -> dict

   Retrieves a document from the specified collection based on its ID.

.. method:: find(self, collection: str, query: dict) -> list

   Retrieves a list of documents from the specified collection based on a query.


