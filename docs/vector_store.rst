Vector Store 
====================

The Dataherald Engine uses a Vector store for retrieving similar few shot examples from previous Natural Language to SQL pairs that have been marked as correct. Currently Pinecone and ChromaDB are the 
supported vector stores, though developers can easily add support for other vector stores by implementing the abstract VectorStore class.

Abstract Vector Store Class
---------------------------

Both ChromaDB and Pinecone are implemented as subclasses of the abstract `VectorStore` class. This abstract class provides a unified interface for working with different vector store implementations.

:class:`VectorStore`
^^^^^^^^^^^^^^^^^^^^^

This abstract class defines the common methods that both ChromaDB and Pinecone vector stores should implement.

.. method:: __init__(self, system: System)

   Initializes the vector store instance.

.. method:: query(self, query_texts: List[str], db_alias: str, collection: str, num_results: int) -> list

   Executes a query to retrieve similar vectors from the vector store.

.. method:: create_collection(self, collection: str)

   Creates a new collection within the vector store.

.. method:: add_record(self, documents: str, collection: str, metadata: Any, ids: List = None)

   Adds vectors along with metadata to a specified collection.

.. method:: delete_record(self, collection: str, id: str)

   Deletes a vector record from a collection.

.. method:: delete_collection(self, collection: str)

   Deletes a collection from the vector store.

By utilizing the `VectorStore` abstract class, you can seamlessly switch between different vector store implementations while maintaining consistent interaction with the underlying systems.

For detailed implementation guidelines and further assistance, consult our official documentation or reach out to our dedicated support team.
