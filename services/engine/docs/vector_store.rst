Vector Store 
====================

The Dataherald Engine uses a Vector store for retrieving similar few shot examples from previous Natural Language to SQL pairs that have been marked as correct. Currently Pinecone, AstraDB, and ChromaDB are the 
supported vector stores, though developers can easily add support for other vector stores by implementing the abstract VectorStore class.

Abstract Vector Store Class
---------------------------

AstraDB, ChromaDB and Pinecone are implemented as subclasses of the abstract :class:`VectorStore` class. This abstract class provides a unified interface for working with different vector store implementations.

:class:`VectorStore`
^^^^^^^^^^^^^^^^^^^^^

This abstract class defines the common methods that AstraDB, ChromaDB, and Pinecone vector stores should implement.

.. method:: __init__(self, system: System)
   :noindex:

   Initializes the vector store instance.

   :param system: The system object.
   :type system: System

.. method:: query(self, query_texts: List[str], db_connection_id: str, collection: str, num_results: int) -> list
   :noindex:

   Executes a query to retrieve similar vectors from the vector store.

   :param query_texts: A list of query texts.
   :type query_texts: List[str]
   :param db_connection_id: The db connection id.
   :type db_connection_id: str
   :param collection: The name of the collection.
   :type collection: str
   :param num_results: The number of results to retrieve.
   :type num_results: int
   :return: A list of retrieved vectors.
   :rtype: list

.. method:: create_collection(self, collection: str)
   :noindex:

   Creates a new collection within the vector store.

   :param collection: The name of the new collection.
   :type collection: str

.. method:: add_record(self, documents: str, collection: str, metadata: Any, ids: List = None)
   :noindex:

   Adds vectors along with metadata to a specified collection.

   :param documents: The vector documents.
   :type documents: str
   :param collection: The name of the collection to which vectors are added.
   :type collection: str
   :param metadata: Metadata associated with the vectors.
   :type metadata: Any
   :param ids: (Optional) A list of identifiers for the records.
   :type ids: List, optional

.. method:: delete_record(self, collection: str, id: str)
   :noindex:

   Deletes a vector record from a collection.

   :param collection: The name of the collection.
   :type collection: str
   :param id: The identifier of the record to delete.
   :type id: str

.. method:: delete_collection(self, collection: str)
   :noindex:

   Deletes a collection from the vector store.

   :param collection: The name of the collection to delete.
   :type collection: str

By utilizing the :class:`VectorStore` abstract class, you can seamlessly switch between different vector store implementations while maintaining consistent interaction with the underlying systems.

For detailed implementation guidelines and further assistance, consult our official documentation or reach out to our dedicated support team.
