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
5. ``golden_records`` - Stores the golden records verfied by the admin or inserted manually by the admin. These are used to augment the prompts and improve the performance of the engine.

Abstract Storage Class
----------------------

All implementations of the Application Storage module must inherit and implement the abstract :class:`DB` class. While MongoDB is the only supported implementation at this time, the abstract class is designed to be easily extended to support other storage solutions.

:class:`DB`
^^^^^^^^^^^^

This abstract class provides a consistent interface for working with different storage solutions.

.. method:: __init__(self, system: System)
   :noindex:

   Initializes the database storage instance.

   :param system: The system object.
   :type system: System

.. method:: insert_one(self, collection: str, obj: dict) -> int
   :noindex:

   Inserts a single document into the specified collection.

   :param collection: The name of the collection.
   :type collection: str
   :param obj: The document to insert.
   :type obj: dict
   :return: The number of documents inserted (usually 1).
   :rtype: int

.. method:: update_or_create(self, collection: str, query: dict, obj: dict) -> int
   :noindex:

   Updates or creates a document in the specified collection based on a query.

   :param collection: The name of the collection.
   :type collection: str
   :param query: The query to find the document to update.
   :type query: dict
   :param obj: The document to update or create.
   :type obj: dict
   :return: The number of documents updated or created.
   :rtype: int

.. method:: find_one(self, collection: str, query: dict) -> dict
   :noindex:

   Retrieves a single document from the specified collection based on a query.

   :param collection: The name of the collection.
   :type collection: str
   :param query: The query to find the document.
   :type query: dict
   :return: The retrieved document.
   :rtype: dict

.. method:: find_by_id(self, collection: str, id: str) -> dict
   :noindex:

   Retrieves a document from the specified collection based on its ID.

   :param collection: The name of the collection.
   :type collection: str
   :param id: The ID of the document to retrieve.
   :type id: str
   :return: The retrieved document.
   :rtype: dict

.. method:: find(self, collection: str, query: dict) -> list
   :noindex:

   Retrieves a list of documents from the specified collection based on a query.

   :param collection: The name of the collection.
   :type collection: str
   :param query: The query to find the documents.
   :type query: dict
   :return: A list of retrieved documents.
   :rtype: list

.. method:: find_all(self, collection: str) -> list
   :noindex:

   Retrieves all documents from the specified collection.

   :param collection: The name of the collection.
   :type collection: str
   :return: A list of retrieved documents.
   :rtype: list

.. method:: delete_by_id(self, collection: str, id: str) -> int
   :noindex:

   Deletes a document from the specified collection based on its ID.

   :param collection: The name of the collection.
   :type collection: str
   :param id: The ID of the document to delete.
   :type id: str
   :return: The number of documents deleted (usually 1).
   :rtype: int
