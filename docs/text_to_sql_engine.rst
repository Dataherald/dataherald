Text-to-SQL Engine Options
==========================

When choosing a text-to-SQL engine for your tasks, various options are available to cater to different requirements. These options include:

- **langchain_sqlagent**: [External Link](https://python.langchain.com/docs/integrations/toolkits/sql_database)
- **langchain_sqlchain**: [External Link](https://js.langchain.com/docs/modules/chains/popular/sqlite)
- **llamaindex_sqlgenerator**: [External Link](https://gpt-index.readthedocs.io/en/v0.6.16/guides/tutorials/sql_guide.html)
- **Dataherald_sqlagent**: Our in-house developed text-to-SQL engine that offers unparalleled accuracy and compatibility with our system.

Choosing Dataherald_sqlagent
----------------------------

Based on an extensive analysis of our internal databases and their corresponding SQL/Question pairs, the Dataherald_sqlagent emerges as the top choice. Its ability to provide highly accurate answers, coupled with its seamless integration with our platform, makes it the recommended option.

Overview of Dataherald_sqlagent
-------------------------------

Our Dataherald_sqlagent is designed to bridge the gap between natural language queries and SQL queries. Utilizing advanced language processing techniques and a deep understanding of database schemas, it efficiently translates user questions into precise SQL queries.

Tools Available to Dataherald_sqlagent
--------------------------------------

The Dataherald_sqlagent is equipped with a range of tools that enhance its capabilities and enable it to provide accurate answers across various scenarios. Depending on the availability of previously verified SQL/Question pairs, the agent has access to 6 or 7 tools:

1. **QuerySQLDataBaseTool**: Executes a given SQL query on the database and returns the string representation of the results.

2. **GetCurrentTimeTool**: Provides access to the current date and time, allowing the agent to address temporal questions, such as "how much did the income increase this month?"

3. **TablesSQLDatabaseTool**: Returns a list of table names, accompanied by a relevance score indicating their potential relevance to the given question.

4. **SchemaSQLDatabaseTool**: Grants access to the schema of the tables, aiding the agent in locating relevant columns.

5. **InfoRelevantColumns**: Offers additional information about specific columns, which can include descriptions from data analysts, categories, and sample rows, enriching the context for query generation.

6. **ColumnEntityChecker**: Facilitates entity searches within specific columns, presenting a list of syntactically relevant entities from the selected column.

7. **GetFewShotExamples**: Allows the agent to request relevant Question/SQL pairs dynamically. The agent can ask for more examples based on question complexity, fostering adaptive learning.

Method Details
--------------

:class:`SQLGenerator`
^^^^^^^^^^^^^^^^^^^^^

This class is a base class that all SQL generation classes inherit from. It provides common methods for generating SQL responses.

.. method:: create_sql_query_status(db, query, response)

   Creates a SQL query status using provided parameters.

.. method:: generate_response(user_question, database_connection, context=None)

   Generates a response to a user question based on the given user question, database connection, and optional context.

For detailed implementation guidelines and further assistance, consult our official documentation or reach out to our dedicated support team.

Conclusion
----------

The Dataherald_sqlagent, with its comprehensive toolset and proven accuracy, is an integral component of our platform. By harnessing its capabilities, you can confidently generate SQL queries from natural language queries and achieve precise answers. For detailed implementation guidelines and further assistance, consult our official documentation or reach out to our dedicated support team.



