API Server Module
=================

The API Server module is responsible for coordinating all other modules and providing APIs to users. Currently, we support FastAPI as our API module, offering a robust and efficient framework for building APIs. FastAPI allows seamless integration with various modules in our system.

Abstract API Class
-------------------

The API Server options, including FastAPI, inherit from the abstract `API` class. This abstract class defines the common methods that all API server solutions should implement.

:class:`API`
^^^^^^^^^^^^

This abstract class provides a consistent interface for interacting with the API server.

.. method:: heartbeat(self) -> int

   Returns the current server time in nanoseconds to check if the server is alive.

.. method:: scan_db(self, scanner_request: ScannerRequest) -> bool

   Initiates the scanning of a database using the provided scanner request.

.. method:: answer_question(self, question_request: QuestionRequest) -> NLQueryResponse

   Provides a response to a user's question based on the provided question request.

.. method:: evaluate_question(self, evaluation_request: EvaluationRequest) -> Evaluation

   Evaluates a generated response to a user's question using the provided evaluation request.

.. method:: connect_database(self, database_connection_request: DatabaseConnectionRequest) -> bool

   Establishes a connection to a database using the provided connection request.

.. method:: add_description(self, db_name: str, table_name: str, table_description_request: TableDescriptionRequest) -> bool

   Adds a description to a specific table within a database based on the provided table description request.

.. method:: add_golden_records(self, golden_records: List) -> bool

   Adds golden records to the vector stores based on the provided list.

.. method:: execute_query(self, query: Query) -> tuple[str, dict]

   Executes a query using the provided Query object and returns the query result.

.. method:: add_data_definition(self, data_definition_request: DataDefinitionRequest) -> bool

   Adds a data definition based on the provided request.

.. method:: update_query(self, query_id: str, query: UpdateQueryRequest) -> NLQueryResponse

   Updates a query using the provided query ID and UpdateQueryRequest.

.. method:: execute_temp_query(self, query_id: str, query: ExecuteTempQueryRequest) -> NLQueryResponse

   Executes a temporary query using the provided query ID and ExecuteTempQueryRequest.

By utilizing the `API` abstract class, you can seamlessly switch between different API server implementations while maintaining consistent interaction with the underlying systems.

For detailed implementation guidelines and further assistance, consult our official documentation or reach out to our dedicated support team.
