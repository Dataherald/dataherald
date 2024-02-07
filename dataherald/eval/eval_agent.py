import logging
import re
import time
from difflib import SequenceMatcher
from typing import Any, Dict, List

from langchain.agents import AgentExecutor
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.chains.llm import LLMChain
from langchain.tools import BaseTool
from langchain.tools.sql_database.tool import (
    BaseSQLDatabaseTool,
    InfoSQLDatabaseTool,
    QuerySQLDataBaseTool,
)
from overrides import override
from pydantic import Field, confloat
from sqlalchemy import MetaData, Table, select

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import Prompt, SQLGeneration

logger = logging.getLogger(__name__)

AGENT_PREFIX: str = """You are a {dialect} expert.
Given a question and a SQL query, analyze the correctness of the SQL query and provide a score as the final answer.
Score indicates how correctly and accurately SQL query answers the question.
Note that the score should be between 0 and 100. Higher scores means the SQL Query is more accurate.
Think step by step to provide the score.
Perform all of the below checks by using the tools:
1) columns used in the SELECT clause should correspond exactly to what user wants.
2) for each of the conditions in the WHERE clause:
    2.1) correct columns should be used to filter the rows (always use entity_finder tool to confirm the correctness)
    2.2) database value used in the condition should handle different scenarios or edge cases
3) all of the calculations should be double checked
4) nested queries and sub-queries should be broken down to simpler parts and all of those part should be checked.
5) the columns used for joining tables must have matching values in both tables
6) execute the given SQL query to check its results and compare it to the expectations
Always predict the score equal to zero if the query returns an empty result.
"""
FORMAT_INSTRUCTIONS = """Use the following format:

Thought: you should always think about what to do
Action: One of the [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the score between 0 and 100 indicating the correctness of the SQL query. score should always be after 'Score:'."""
AGENT_SUFFIX: str = """How accurately the SQL query can answer the question?
Give me a score between 0 and 100 by performing a step by step evaluation.
Question: {question}
SQL: {SQL}
"""


class EntityFinder(BaseSQLDatabaseTool, BaseTool):
    """Tool finding all syntactically similar entites from a database"""

    name = "entity_finder"
    description = """
    Input to this tool is an enitity, a column, and the table containing the column.
    All the rows that have similar values to the given entity are returned.
    If the entity is not found, a not found message will be returned.
    Use this tool to check the correctness of conditions used in the WHERE clause.

    Input format: entity, column_name, table_name

    Example Input: David, name, singer
    """
    similarity_threshold: confloat(ge=0, le=1) = 0.7
    number_similar_items: int = 20

    def similarity(self, first_string: str, second_string: str) -> float:
        return SequenceMatcher(None, first_string, second_string).ratio()

    def _run(
        self,
        input: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        try:
            response = ""
            entity, column_name, table_name = input.split(", ")
            engine = self.db._engine

            metadata = MetaData(bind=engine)
            table = Table(table_name, metadata, autoload=True)
            column = table.c[column_name]

            query = select(column.distinct()).select_from(table)

            # Execute the query and fetch all rows
            with engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()

            # Process the retrieved rows as needed
            similar_items = []
            for row in rows:
                pair_similarity = self.similarity(entity, str(row[0]))
                if pair_similarity > self.similarity_threshold:
                    similar_items.append({"row": str(row[0]), "score": pair_similarity})
            similar_items = sorted(
                similar_items, key=lambda x: x["score"], reverse=True
            )[: self.number_similar_items]
            for item in similar_items:
                response += f"Column {column_name}, contains -> {item['row']}.\n"

            if not response:
                response = f"Column {column_name} doesn't contain any value similar to {entity}"

            return response
        except Exception as e:
            return str(e)

    async def _arun(
        self,
        query: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("QuerySqlDbTool does not support async")


class SQLEvaluationToolkit(BaseToolkit):
    """Toolkit for interacting with SQL databases for the evaluation of the SQL Query"""

    db: SQLDatabase = Field(exclude=True)

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        info_sql_database_tool_description = (
            "Input to this tool is a comma-separated list of tables, output is the schema and sample first rows for those tables."
            "Use this tool to find the columns inside each table and their sample rows."
            "Example Input: table1, table2, table3"
        )
        info_sql_database_tool = InfoSQLDatabaseTool(
            db=self.db, description=info_sql_database_tool_description
        )
        query_sql_database_tool_description = (
            "Input to this tool is a SQL query, output is a result from the database. If the query is not correct, an error message "
            "will be returned. If an error is returned, rewrite the query and try again. If you encounter an issue with Unknown column "
            f"'xxxx' in 'field list', using {info_sql_database_tool.name} "
            "to query the correct table fields."
            "Use this tool to search for a specific value or to check a specific condition in the database."
        )
        query_sql_database_tool = QuerySQLDataBaseTool(
            db=self.db, description=query_sql_database_tool_description
        )
        entity_finder = EntityFinder(db=self.db)
        return [query_sql_database_tool, info_sql_database_tool, entity_finder]


class EvaluationAgent(Evaluator):
    sample_rows: int = 10
    llm: Any = None

    def __init__(self, system: System):
        super().__init__(system)
        self.system = system

    def answer_parser(self, answer: str) -> int:
        """
        Extract the number after the Score:
        If not found extract the last number between 0 and 100
        If not found return 0
        """
        pattern = r".*Score:\s*(\d+)"
        match = re.search(pattern, answer)
        output = 0
        if match:
            output = int(match.group(1))
        else:
            pattern = r"\b([0-9]{1,2}|100)\b"
            numbers = re.findall(pattern, answer)
            if numbers:
                output = int(numbers[-1])
        return output

    def create_evaluation_agent(
        self,
        toolkit: SQLEvaluationToolkit,
        database_connection: DatabaseConnection,
        prefix: str = AGENT_PREFIX,
        suffix: str = AGENT_SUFFIX,
        callback_manager: BaseCallbackManager | None = None,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: List[str] | None = None,
        max_iterations: int | None = 15,
        max_execution_time: float | None = None,
        early_stopping_method: str = "force",
        verbose: bool = False,
        agent_executor_kwargs: Dict[str, Any] | None = None,
        **kwargs: Dict[str, Any],
    ) -> AgentExecutor:
        database = SQLDatabase.get_sql_engine(database_connection)
        tools = toolkit.get_tools()
        prefix = prefix.format(dialect=database.dialect)
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            format_instructions=format_instructions,
            input_variables=input_variables,
        )
        llm_chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            callback_manager=callback_manager,
        )
        tool_names = [tool.name for tool in tools]
        agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            callback_manager=callback_manager,
            verbose=verbose,
            max_iterations=max_iterations,
            max_execution_time=max_execution_time,
            early_stopping_method=early_stopping_method,
            **(agent_executor_kwargs or {}),
        )

    @override
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        start_time = time.time()
        logger.info(
            f"Generating score for the question/sql pair: {str(user_prompt.text)}/ {str(sql_generation.sql)}"
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=self.llm_config.llm_name,
            api_base=self.llm_config.api_base,
        )
        database = SQLDatabase.get_sql_engine(database_connection)
        user_question = user_prompt.text
        sql = sql_generation.sql
        database._sample_rows_in_table_info = self.sample_rows
        toolkit = SQLEvaluationToolkit(db=database)
        agent_executor = self.create_evaluation_agent(
            toolkit=toolkit,
            database_connection=database_connection,
            verbose=True,
            input_variables=["question", "SQL"],
        )
        answer = agent_executor.invoke({"question": user_question, "SQL": sql})[
            "output"
        ]
        score = self.answer_parser(answer=answer) / 100
        end_time = time.time()
        logger.info(f"Evaluation time elapsed: {str(end_time - start_time)}")
        return Evaluation(
            question_id=user_prompt.id, answer_id=sql_generation.id, score=score
        )
