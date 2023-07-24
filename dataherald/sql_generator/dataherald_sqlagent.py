import logging
from typing import Any, Dict, List

import numpy as np
import openai
import pandas as pd
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.chains.llm import LLMChain
from langchain.schema import AgentAction
from langchain.tools.base import BaseTool
from overrides import override
from pydantic import BaseModel, Extra, Field

from dataherald.context_store import ContextStore
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import (
    DatabaseConnection,
    TableSchemaDetail,
    get_mock_table_schema_detail,
)
from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


AGENT_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
#
Here is the process to follow for the given input question:
1) Identify the relevant tables related to the question.
2) Retrieve the schema of the relevant tables to determine potentially relevant columns.
3) Gather more information about the possibly relevant columns, filtering them to find the relevant ones.
4) Always Obtain a few examples of Question/SQL pairs to understand the task and columns relationships better.
5) Execute the SQL query on the database to obtain the results.
#
Some tips:
tip1) For complex questions that has many relevant columns and tables request for more examples of Question/SQL pairs.
tip2) The maximum number of Question/SQL pairs you can request is {max_examples}.
tip3) If the SQL query resulted in errors, rewrite the SQL query and try again.
tip4) If you are still unsure about which columns and tables to use, ask for more examples.
#
If the question does not seem related to the database, just return "I don't know" as the answer.
"""

FORMAT_INSTRUCTIONS = """Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

AGENT_SUFFIX = """Begin!

Question: {input}
Thought: I should look at the tables in the database to see which of them are related to the question.
{agent_scratchpad}"""


# Classes needed for tools
class BaseSQLDatabaseTool(BaseModel):
    """Base tool for interacting with the SQL database and the context information."""

    db: SQLDatabase = Field(exclude=True)
    context: List[dict] = Field(exclude=True)

    class Config(BaseTool.Config):
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True
        extra = Extra.forbid


class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name = "sql_db_query"
    description = """
    Input: SQL query.
    Output: Result from the database or an error message if the query is incorrect.
    If an error occurs, rewrite the query and retry.
    Use this tool to execute SQL queries.
    """

    def _run(
        self,
        query: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        return self.db.run_no_throw(query)

    async def _arun(
        self,
        query: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("DBQueryTool does not support async")


class TablesSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool which takes in the given question and returns a list of tables with their relevance score to the question"""

    name = "db_tables_with_relevance_scores"
    description = """
    Input: Given question.
    Output: Comma-separated list of tables with their relevance scores, indicating their relevance to the question.
    Use this tool to identify the relevant tables for the given question.
    """
    db_scan: List[TableSchemaDetail]

    def get_embedding(
        self, text: str, model: str = "text-embedding-ada-002"
    ) -> List[float]:
        text = text.replace("\n", " ")
        return openai.Embedding.create(input=[text], model=model)["data"][0][
            "embedding"
        ]

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        return round(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), 4)

    def _run(
        self,
        user_question: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Use the concatenation of table name, columns names, and the description of the table as the table representation"""
        question_embedding = self.get_embedding(user_question)
        table_representations = []
        for table in self.db_scan:
            col_rep = ""
            for column in table.columns:
                col_rep += column.name + " "
            table_rep = f"Table {table.table_name} contain columns: {col_rep}, this tables has: {table.description}"
            table_representations.append([table.table_name, table_rep])
        df = pd.DataFrame(
            table_representations, columns=["table_name", "table_representation"]
        )
        df["table_embedding"] = df.table_representation.apply(
            lambda x: self.get_embedding(x)
        )
        df["similarities"] = df.table_embedding.apply(
            lambda x: self.cosine_similarity(x, question_embedding)
        )
        table_relevance = ""
        for _, row in df.iterrows():
            table_relevance += (
                f'Table: {row["table_name"]}, relevance score: {row["similarities"]}\n'
            )
        return table_relevance

    async def _arun(
        self,
        user_question: str = "",
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError(
            "TablesWithRelevanceScoresTool does not support async"
        )


class SchemaSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting schema of relevant tables."""

    name = "db_relevant_tables_schema"
    description = """
    Input: Comma-separated list of tables.
    Output: Schema of the specified tables.
    Use this tool to discover all columns of the relevant tables and identify potentially relevant columns.

    Example Input: table1, table2, table3
    """
    db_scan: List[TableSchemaDetail]

    def _run(
        self,
        table_names: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        table_names_list = table_names.split(", ")
        tables_schema = ""
        for table in self.db_scan:
            if table.table_name in table_names_list:
                tables_schema += table.table_schema + "\n"
        if tables_schema == "":
            tables_schema += "Tables not found in the database"
        return tables_schema

    async def _arun(
        self,
        table_name: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("DBRelevantTablesSchemaTool does not support async")


class InfoRelevantColumns(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting more information for potentially relevant columns"""

    name = "db_relevant_columns_info"
    description = """
    Input: Comma-separated list of potentially relevant columns with their corresponding table.
    Output: Information about the values inside the columns and their descriptions.
    Use this tool to gather details about potentially relevant columns. then, filter them, and identify the relevant ones.

    Example Input: table1 -> column1, table1 -> column2, table2 -> column1
    """
    db_scan: List[TableSchemaDetail]

    def _run(
        self,
        column_names: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        items_list = column_names.split(", ")
        column_full_info = ""
        for item in items_list:
            table_name, column_name = item.split(" -> ")
            found = False
            for table in self.db_scan:
                if table_name == table.table_name:
                    col_info = ""
                    for column in table.columns:
                        if column_name == column.name:
                            found = True
                            col_info += f"Description: {column.description},"
                            if column.low_cardinality:
                                col_info += f" categories = {column.categories},"
                    col_info += " Sample rows: "
                    for row in table.examples:
                        col_info += row[column_name] + ", "
                    col_info = col_info[:-2]
                    column_full_info += f"Table: {table_name}, column: {column_name}, additional info: {col_info}\n"
            if not found:
                column_full_info += f"Table: {table_name}, column: {column_name} not found in database\n"
        return column_full_info

    async def _arun(
        self,
        table_name: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("InfoRelevantColumnsTool does not support async")


class GetFewShotExamples(BaseSQLDatabaseTool, BaseTool):
    """Tool to obtain few-shot examples from the pool of samples"""

    name = "fewshot_examples_retriever"
    description = """
    Input: Number of required examples.
    Output: List of similar questions with their SQL queries.
    Use this tool to fetch previously asked Question/SQL pairs as examples for improving SQL query generation.
    For complex questions, request more examples to gain a better understanding of tables and columns.
    Use this tool before generating SQL queries.
    """
    few_shot_examples: List[dict]

    def _run(
        self,
        number_of_samples: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        if number_of_samples.isdigit():
            number_of_samples = int(number_of_samples)
        else:
            return "Action input for the fewshot_examples_retriever tool should be an integer"
        returned_output = ""
        for example in self.few_shot_examples[:number_of_samples]:
            if "used" not in example:
                returned_output += f"Question: {example['nl_question']} -> SQL: {example['sql_query']}\n"
                example["used"] = True
        if returned_output == "":
            returned_output = "No previously asked Question/SQL pairs are available"
        return returned_output

    async def _arun(
        self,
        number_of_samples: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("GetFewShotExamplesTool does not support async")


class SQLDatabaseToolkit(BaseToolkit):
    """Dataherald toolkit"""

    db: SQLDatabase = Field(exclude=True)
    context: List[dict] = Field(exclude=True)
    few_shot_examples: List[dict] = Field(exclude=True)
    db_scan: List[TableSchemaDetail] = Field(exclude=True)

    @property
    def dialect(self) -> str:
        """Return string representation of SQL dialect to use."""
        return self.db.dialect

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        query_sql_db_tool = QuerySQLDataBaseTool(db=self.db, context=self.context)
        tables_sql_db_tool = TablesSQLDatabaseTool(
            db=self.db, context=self.context, db_scan=self.db_scan
        )
        schema_sql_db_tool = SchemaSQLDatabaseTool(
            db=self.db, context=self.context, db_scan=self.db_scan
        )
        info_relevant_tool = InfoRelevantColumns(
            db=self.db, context=self.context, db_scan=self.db_scan
        )
        get_fewshot_examples_tool = GetFewShotExamples(
            db=self.db, context=self.context, few_shot_examples=self.few_shot_examples
        )
        return [
            query_sql_db_tool,
            tables_sql_db_tool,
            schema_sql_db_tool,
            info_relevant_tool,
            get_fewshot_examples_tool,
        ]


class DataheraldSQLAgent(SQLGenerator):
    """Dataherald SQL agent"""

    max_number_of_examples: int = 100  # maximum number of question/SQL pairs

    def remove_duplicate_examples(self, fewshot_exmaples: List[dict]) -> List[dict]:
        returned_result = []
        seen_list = []
        for example in fewshot_exmaples:
            if example["nl_question"] not in seen_list:
                seen_list.append(example["nl_question"])
                returned_result.append(example)
        return returned_result

    def create_sql_agent(
        self,
        toolkit: SQLDatabaseToolkit,
        callback_manager: BaseCallbackManager | None = None,
        prefix: str = AGENT_PREFIX,
        suffix: str | None = None,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: List[str] | None = None,
        max_examples: int = 20,
        top_k: int = 10,
        max_iterations: int | None = 15,
        max_execution_time: float | None = None,
        early_stopping_method: str = "force",
        verbose: bool = False,
        agent_executor_kwargs: Dict[str, Any] | None = None,
        **kwargs: Dict[str, Any],
    ) -> AgentExecutor:
        """Construct an SQL agent from an LLM and tools."""
        tools = toolkit.get_tools()
        prefix = prefix.format(
            dialect=toolkit.dialect, top_k=top_k, max_examples=max_examples
        )
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix or AGENT_SUFFIX,
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
    def generate_response(
        self,
        user_question: NLQuery,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
    ) -> NLQueryResponse:
        context_store = self.system.instance(ContextStore)
        db_scan = get_mock_table_schema_detail()
        few_shot_examples = context_store.retrieve_context_for_question(
            user_question, number_of_samples=self.max_number_of_examples
        )
        new_fewshot_examples = self.remove_duplicate_examples(few_shot_examples)
        logger.info(f"Generating SQL response to question: {str(user_question.dict())}")
        self.database = SQLDatabase.get_sql_engine(database_connection)
        toolkit = SQLDatabaseToolkit(
            db=self.database,
            context=context,
            few_shot_examples=new_fewshot_examples,
            db_scan=db_scan,
        )
        agent_executor = self.create_sql_agent(
            toolkit=toolkit,
            verbose=True,
            max_examples=len(new_fewshot_examples),
        )
        agent_executor.return_intermediate_steps = True
        agent_executor.handle_parsing_errors = (True,)
        result = agent_executor({"input": user_question.question})
        intermediate_steps = []
        sql_query_list = []
        for step in result["intermediate_steps"]:
            action = step[0]
            if type(action) == AgentAction and action.tool == "sql_db_query":
                sql_query_list.append(action.tool_input)

            intermediate_steps.append(str(step))

        return NLQueryResponse(
            nl_question_id=user_question.id,
            nl_response=result["output"],
            intermediate_steps=intermediate_steps,
            sql_query=sql_query_list[-1] if len(sql_query_list) > 0 else "",
        )
