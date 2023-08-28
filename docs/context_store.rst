Context Store
====================

The Context Store module is responsible for storing and retrieving context about the connected Databases and the business logic of the stored data.
This information is subsequently accessed and used by the Text-to-SQL module for prompt engineering to generate accurate SQL to answer the natural 
language question. 


There is currently a single implementation of the Context Store which accesses both the Vector store and Application Storage
componenets to store and find closest validated SQL queries and information about the DB tables and rows. 


Abstract Context Store Class
-----------------------------
All implementations of the context store must inherit from the abstract ``ContextStore`` class and implement the following methods.


Context Retrieval
~~~~~~~~~~~~~~~~~~

.. py:function:: retrieve_context_for_question(nl_question: str) -> str

   Given a natural language question, this method retrieves a single string containing information about relevant data stores, tables, and columns necessary for building the SQL query. This information includes example questions, corresponding SQL queries, and metadata about the tables (e.g., categorical columns). The retrieved string is then passed to the text-to-SQL generator.

   :param nl_question: The natural language question.
   :type nl_question: str
   :return: A string containing context information for generating SQL.
   :rtype: str

Managing Golden SQL 
~~~~~~~~~~~~~~~~~~~~

The Context Store also provides methods for adding and removing different types of context to the store. 
The initial context type involves adding NL<>SQL pairs as examples that will be used in prompts for the Language Model.

.. py:function:: add_golden_records(golden_records: List[GoldenRecordRequest]) -> List[GoldenRecord]
   :noindex:

   This method adds NL<>SQL pairs to the context store. These pairs serve as examples and will be included in prompts to the Language Model.

   :param golden_records: A list of natural language questions and the SQL that can be used to answer them.
   :type golden_records: List[GoldenRecordRequest]
   :return: A list of GoldenRecord objects that were added to the context store.
   :rtype: List[GoldenRecord]



.. py:function:: remove_golden_records(self, ids: List) -> bool:

   This method removes NL <> SQL pairs that were stored in the context store so they are not used in few shot prompting.

   :param ids: A list of ids of the golden records to be removed.
   :type ids: List
   :return: True if the records were successfully removed
   :rtype: bool
