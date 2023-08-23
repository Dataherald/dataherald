Vector Store 
====================

In our system, we currently support two commonly used vector stores: ChromaDB and Pinecone. Each vector store offers distinct features and advantages that cater to different use cases.

ChromaDB
--------

ChromaDB is a powerful vector database that provides efficient storage and retrieval of high-dimensional vectors. Its advantages include:

- **Local Storage**: ChromaDB stores vectors in a local database, ensuring fast access and low-latency queries.
- **Flexible Schema**: ChromaDB allows for flexible schema designs, making it suitable for a variety of vector types and applications.
- **Efficient Indexing**: ChromaDB employs advanced indexing techniques to accelerate vector similarity searches, enabling quick and accurate retrieval of similar vectors.

Pinecone
--------

Pinecone is a cloud-based vector search engine that specializes in delivering high-performance vector search capabilities. Its advantages include:

- **Scalability**: Pinecone offers seamless scalability, enabling you to handle large-scale vector datasets and dynamic workloads.
- **Real-time Search**: Pinecone is optimized for real-time vector search, making it suitable for applications that require low-latency retrieval of similar vectors.
- **API-Driven**: Pinecone provides a comprehensive API that allows you to integrate vector search capabilities into your applications with ease.

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
