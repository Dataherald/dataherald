Text-to-SQL Engine
==========================

The Text-to-SQL agent is a core module which translates the Natural Language question received through the ``/question`` endpoint to SQL. The implementation can leverage business and data logic stored in the Context Store module. 
to generate accurate SQL given the DB schema. Currently the following NL-to-SQL implementations are included in the codebase:

- ``Langchain SQL Agent`` - A wrapper around the `Langchain SQLAgent <https://python.langchain.com/docs/integrations/toolkits/sql_database>`_ 
- ``Langchain SQL Chain`` - A wrapper around the `Langchain SQLChain <https://python.langchain.com/docs/integrations/tools/sqlite>`_
- ``LlamaIndex SQL Generator`` - A wrapper around the `LlamaIndex SQL Generator <https://gpt-index.readthedocs.io/en/v0.6.16/guides/tutorials/sql_guide.html>`_
- ``Dataherald SQL Agent`` - Our in-house Natural Language-to-SQL agent which uses uses in-context learning 
 

Dataherald SQL Agent
---------------------------------

The ``dataherald_sqlagent`` is an agent that outperforms the Langchain SQL Agent by 12%-250% in our benchmarking. It does this by leveraging up to 
7 tools to generate valid SQL:     

1. **QuerySQLDataBaseTool**: Executes a given SQL query on the database and returns the string representation of the results.

2. **GetCurrentTimeTool**: Provides access to the current date and time, allowing the agent to address temporal questions, such as "how much did the income increase this month?"

3. **TablesSQLDatabaseTool**: Returns a list of table names, accompanied by a relevance score indicating their potential relevance to the given question.

4. **SchemaSQLDatabaseTool**: Grants access to the schema of the tables, aiding the agent in locating relevant columns.

5. **InfoRelevantColumns**: Offers additional information about specific columns, which can include descriptions from data analysts, categories, and sample rows, enriching the context for query generation.

6. **ColumnEntityChecker**: Facilitates entity searches within specific columns, presenting a list of syntactically relevant entities from the selected column.

7. **GetFewShotExamples**: Allows the agent to request relevant Question/SQL pairs dynamically. The agent can ask for more examples based on question complexity, fostering adaptive learning.



Abstract SQLGenerator Class
---------------------------

Base class that all SQL generation classes inherit from.

:class:`SQLGenerator`
^^^^^^^^^^^^^^^^^^^^^

This base class defines the common structure for SQL generation classes.

.. method:: create_sql_query_status(db, query, response, top_k)
   :noindex:

   Creates a SQL query status using provided parameters.

   :param db: The SQL database instance.
   :type db: SQLDatabase
   :param query: The SQL query.
   :type query: str
   :param response: The Response instance.
   :type response: Response
   :param top_k: The number of results to return.
   :type top_k: int
   :return: The updated Response instance with the SQL query status.
   :rtype: Response

.. method:: generate_response(user_question, database_connection, context=None)
   :noindex:

   Generates a response to a user question based on the given user question, database connection, and optional context.

   :param user_question: The user's natural language question.
   :type user_question: Question
   :param database_connection: The database connection information.
   :type database_connection: DatabaseConnection
   :param context: (Optional) Additional context information.
   :type context: List[dict], optional
   :return: The Response containing the generated response.
   :rtype: Response





