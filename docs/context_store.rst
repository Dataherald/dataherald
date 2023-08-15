Context Store Module
====================

The Context Store module is responsible for managing a vector database that stores relevant information for accurately generating SQL queries based on natural language prompts.

Context Retrieval
------------------

.. py:function:: retrieve_context_for_question(nl_question: str) -> str

   Given a natural language question, this method retrieves a single string containing information about relevant data stores, tables, and columns necessary for building the SQL query. This information includes example questions, corresponding SQL queries, and metadata about the tables (e.g., categorical columns). The retrieved string is then passed to the text-to-SQL generator.

   :param nl_question: The natural language question.
   :type nl_question: str
   :return: A string containing context information for generating SQL.
   :rtype: str

Context Addition
-----------------

The Context Store also provides methods for adding different types of context to the store. The initial context type involves adding NL<>SQL pairs as examples that will be used in prompts for the Language Model.

.. py:function:: add_context_store_golden_sql(nl_2_sql_list: List)

   This method adds NL<>SQL pairs to the context store. These pairs serve as examples and will be included in prompts to the Language Model.

   :param nl_2_sql_list: List of NL<>SQL pairs.
   :type nl_2_sql_list: List
