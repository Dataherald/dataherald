API Module
=================

The API module implements the controller logic that orchestrates module calls once API calls are made and also sets up the server that exposes the APIs. Currently, FastAPI is the only supported API server implementation.

Abstract API Class
-------------------

The API Server options, including FastAPI, inherit from the abstract :class:`API` class. The following are required methods that need to be implemented.

:class:`API`
^^^^^^^^^^^^

All implementations of the API module must inherit and implement the abstract :class:`API` class. 

.. method:: heartbeat(self) -> int
   :noindex:

   Returns the current server time in nanoseconds to check if the server is alive.

   :return: The current server time in nanoseconds.
   :rtype: int

.. method:: scan_db(self, scanner_request: ScannerRequest) -> bool
   :noindex:

   Initiates the scanning of a database using the provided scanner request.

   :param scanner_request: The scanner request.
   :type scanner_request: ScannerRequest
   :return: True if the scanning was initiated successfully; otherwise, False.
   :rtype: bool

.. method:: answer_question(self, question_request: QuestionRequest) -> Response
   :noindex:

   Provides a response to a user's question based on the provided question request.

   :param question_request: The question request.
   :type question_request: QuestionRequest
   :return: The Response containing the response to the user's question.
   :rtype: Response

.. method:: create_database_connection(self, database_connection_request: DatabaseConnectionRequest) -> bool
   :noindex:

   Establishes a connection to a database using the provided connection request.

   :param database_connection_request: The database connection request.
   :type database_connection_request: DatabaseConnectionRequest
   :return: True if the connection was established successfully; otherwise, False.
   :rtype: bool

.. method:: add_description(self, db_connection_id: str, table_name: str, table_description_request: TableDescriptionRequest) -> bool
   :noindex:

   Adds a description to a specific table within a database based on the provided table description request.

   :param db_connection_id: The db connection id
   :type db_connection_id: str
   :param table_name: The name of the table.
   :type table_name: str
   :param table_description_request: The table description request.
   :type table_description_request: TableDescriptionRequest
   :return: True if the description was added successfully; otherwise, False.
   :rtype: bool

.. method:: add_golden_records(self, golden_records: List[GoldenRecordRequest]) -> List[GoldenRecord]
   :noindex:

   Adds golden records to the vector stores based on the provided list.

   :param golden_records: A list of golden record requests.
   :type golden_records: List[GoldenRecordRequest]
   :return: A list of added GoldenRecord objects.
   :rtype: List[GoldenRecord]

.. method:: execute_query(self, query: Query) -> tuple[str, dict]
   :noindex:

   Executes a query using the provided Query object and returns the query result.

   :param query: The query to execute.
   :type query: Query
   :return: A tuple containing the query status and result.
   :rtype: tuple[str, dict]

.. method:: update_query(self, query_id: str, query: UpdateQueryRequest) -> Response
   :noindex:

   Updates a query using the provided query ID and UpdateQueryRequest.

   :param query_id: The ID of the query to update.
   :type query_id: str
   :param query: The update query request.
   :type query: UpdateQueryRequest
   :return: The Response containing the result of the query update.
   :rtype: Response

.. method:: execute_temp_query(self, query_id: str, query: CreateResponseRequest) -> Response
   :noindex:

   Executes a temporary query using the provided query ID and CreateResponseRequest.

   :param question_id: The ID of the question to execute.
   :type question_id: str
   :param query: The query request.
   :type query: CreateResponseRequest
   :return: The Response containing the result.
   :rtype: Response

.. method:: get_scanned_databases(self, db_connection_id: str) -> ScannedDBResponse
   :noindex:

   Retrieves information about scanned databases based on a database connection id.

   :param db_connection_id: The database connection id.
   :type db_connection_id: str
   :return: The ScannedDBResponse containing information about scanned databases.
   :rtype: ScannedDBResponse

.. method:: delete_golden_record(self, golden_record_id: str) -> dict
   :noindex:

   Deletes a golden record based on its ID.

   :param golden_record_id: The ID of the golden record to delete.
   :type golden_record_id: str
   :return: A dictionary containing information about the deleted golden record.
   :rtype: dict

.. method:: get_golden_records(self, page: int = 1, limit: int = 10) -> List[GoldenRecord]
   :noindex:

   Retrieves a list of golden records with pagination support.

   :param page: The page number (default is 1).
   :type page: int
   :param limit: The maximum number of records per page (default is 10).
   :type limit: int
   :return: A list of retrieved GoldenRecord objects.
   :rtype: List[GoldenRecord]

