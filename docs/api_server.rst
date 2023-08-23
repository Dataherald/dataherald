API Module
=================

The API module implements the controller that orchestrates component calls once API calls are made and also sets up the server that exposes the APIs. Currently, FastAPI is the only supported API server implementation.

Abstract API Class
-------------------

The API Server options, including FastAPI, inherit from the abstract `API` class. The following are required methods that need to be implemented.

:class:`API`
^^^^^^^^^^^^

All implementations of the API module must inherit and implement the abstract `API` class. 

.. method:: heartbeat(self) -> int

   Returns the current server time in nanoseconds to check if the server is alive.

.. method:: scan_db(self, scanner_request: ScannerRequest) -> bool

   Initiates the scanning of a database using the provided scanner request.

.. method:: answer_question(self, question_request: QuestionRequest) -> NLQueryResponse

   Provides a response to a user's question based on the provided question request.

.. method:: connect_database(self, database_connection_request: DatabaseConnectionRequest) -> bool

   Establishes a connection to a database using the provided connection request.

.. method:: add_description(self, db_name: str, table_name: str, table_description_request: TableDescriptionRequest) -> bool

   Adds a description to a specific table within a database based on the provided table description request.

.. method:: add_golden_records(self, golden_records: List) -> bool

   Adds golden records to the vector stores based on the provided list.

.. method:: execute_query(self, query: Query) -> tuple[str, dict]

   Executes a query using the provided Query object and returns the query result.

.. method:: update_query(self, query_id: str, query: UpdateQueryRequest) -> NLQueryResponse

   Updates a query using the provided query ID and UpdateQueryRequest.

.. method:: execute_temp_query(self, query_id: str, query: ExecuteTempQueryRequest) -> NLQueryResponse

   Executes a temporary query using the provided query ID and ExecuteTempQueryRequest.


