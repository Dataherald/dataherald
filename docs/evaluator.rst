Evaluation Module
====================

The Evaluation Module is called as a post-processing step after SQL query generation. It assigns a confidence level between 0 and 1 to the generated SQL query. 
Different methods can be used to assign this score using LLM Confidence and Uncertainty values, topics which are outside the scope of this documentation.

There are currently two implementations of the Evaluation Module in the repo: the ``EvaluationAgent`` and the ``SimpleEvaluator``.




EvaluationAgent
-------------------------

The "EvaluationAgent" method utilizes an agent that interacts with a set of tools to generate evaluation scores. This method involves the following steps:

1. **InfoSQLDatabaseTool**: This tool takes a list of tables as input and returns the schema along with sample rows for the given tables.

2. **QuerySQLDataBaseTool**: This tool runs a provided query on the database.

3. **EntityFinder**: This tool checks the existence of a given entity within a column.

Due to the reliance on these tools and the need to interact with them, the evaluation process takes around 40 to 50 seconds to evaluate a single query.

SimpleEvaluator
--------------------------

The "SimpleEvaluator" method is implemented using LLMs and is designed to be much faster compared to the "EvaluationAgent" method. In this method:

1. A list of common problems associated with SQL queries is provided to the model.
2. The model checks the generated query against all of these common issues.
3. The evaluation process doesn't require interactions with external tools.

This method is preferred when speed is crucial, as it doesn't involve tool interactions.




Abstract Evaluator Class
-----------------------------
All implementations of the Evaluation component must inherit from the ``Evaluator`` abstract class and implement the following methods:


.. py:class:: Evaluation

   Represents the evaluation result with attributes.

   :param id: The evaluation's ID.
   :type id: str
   :param question_id: The associated question's ID.
   :type question_id: str
   :param answer_id: The associated answer's ID.
   :type answer_id: str
   :param score: The confidence score, ranging from 0 to 1.
   :type score: float

.. py:class:: Evaluator(Component, ABC)

   An abstract base class for evaluators.

   :param database: The SQLDatabase instance for evaluation.
   :type database: SQLDatabase
   :param acceptance_threshold: The threshold for accepting generated responses.
   :type acceptance_threshold: float
   :param system: The system containing the evaluator.
   :type system: System

   .. py:method:: get_confidence_score(question, generated_answer, database_connection)

      Determines if a generated response from the engine is acceptable based on the ACCEPTANCE_THRESHOLD.

      :param question: The natural language question.
      :type question: Question
      :param generated_answer: The generated SQL query response.
      :type generated_answer: Response
      :param database_connection: The database connection.
      :type database_connection: DatabaseConnection
      :return: The confidence score.
      :rtype: float

   .. py:method:: evaluate(question, generated_answer, database_connection)

      Abstract method to evaluate a question with an SQL pair. Subclasses must implement this method.

      :param question: The natural language question.
      :type question: Question
      :param generated_answer: The generated SQL query response.
      :type generated_answer: Response
      :param database_connection: The database connection.
      :type database_connection: DatabaseConnection
      :return: An Evaluation instance.
      :rtype: Evaluation
