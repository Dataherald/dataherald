import datetime
import difflib
import logging
import time
from typing import Any, Callable, Dict, List

import numpy as np
import openai
import pandas as pd
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.callbacks import get_openai_callback
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
from sqlalchemy.exc import SQLAlchemyError

from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.db_scanner.models.types import TableSchemaDetail
from dataherald.db_scanner.repository.base import DBScannerRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import (
    DatabaseConnection,
)
from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


AGENT_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
#
Here is the plan you have to follow:
1) Use the fewshot_examples_retriever tool to retrieve a first set of possibly relevant tables and columns and the SQL syntax to use.
2) Use the db_tables_with_relevance_scores tool to find the a second set of possibly relevant tables.
3) Use the db_relevant_tables_schema tool to obtain the schema of the both sets of possibly relevant tables to identify the possibly relevant columns.
4) Use the db_relevant_columns_info tool to gather more information about the possibly relevant columns, filtering them to find the relevant ones.
5) [Optional based on the question] Use the get_current_datetime tool if the question has any mentions of time or dates.
6) [Optional based on the question] Always use the db_column_entity_checker tool to make sure that relevant columns have the cell-values.
7) Write a {dialect} query and use sql_db_query tool the Execute the SQL query on the database to obtain the results.
#
Some tips to always keep in mind:
tip1) For complex questions that has many relevant columns and tables request for more examples of Question/SQL pairs.
tip2) The maximum number of Question/SQL pairs you can request is {max_examples}.
tip3) If the SQL query resulted in errors, rewrite the SQL query and try again.
tip4) If you are still unsure about which columns and tables to use, ask for more Question/SQL pairs.
tip5) The Question/SQL pairs are labelled as correct pairs, so you can use them to learn how to construct the SQL query.
#
Always use the get_current_datetime tool if there is any time or date in the given question.
If the question does not seem related to the database, just return "I don't know" as the answer.
If the there is a very similar question among the fewshot examples, modify the SQL query to fit the given question and return the answer.
The SQL query MUST have in-line comments to explain what each clause does.
"""  # noqa: E501

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
Thought: I should Collect examples of Question/SQL pairs to identify possibly relevant tables, columns, and SQL query styles. If there is a similar question among the examples, I can use the SQL query from the example and modify it to fit the given question.
{agent_scratchpad}"""  # noqa: E501


def catch_exceptions(fn: Callable[[str], str]) -> Callable[[str], str]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: PLR0911
        try:
            return fn(*args, **kwargs)
        except openai.error.APIError as e:
            # Handle API error here, e.g. retry or log
            return f"OpenAI API returned an API Error: {e}"
        except openai.error.APIConnectionError as e:
            # Handle connection error here
            return f"Failed to connect to OpenAI API: {e}"
        except openai.error.RateLimitError as e:
            # Handle rate limit error (we recommend using exponential backoff)
            return f"OpenAI API request exceeded rate limit: {e}"
        except openai.error.Timeout as e:
            # Handle timeout error (we recommend using exponential backoff)
            return f"OpenAI API request timed out: {e}"
        except openai.error.ServiceUnavailableError as e:
            # Handle service unavailable error (we recommend using exponential backoff)
            return f"OpenAI API service unavailable: {e}"
        except openai.error.InvalidRequestError as e:
            return f"OpenAI API request was invalid: {e}"
        except SQLAlchemyError as e:
            return f"An unknown error occurred: {e}"

    return wrapper


# Classes needed for tools
class BaseSQLDatabaseTool(BaseModel):
    """Base tool for interacting with the SQL database and the context information."""

    db: SQLDatabase = Field(exclude=True)
    context: List[dict] | None = Field(exclude=True, default=None)

    class Config(BaseTool.Config):
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True
        extra = Extra.forbid


class GetCurrentTimeTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name = "get_current_datetime"
    description = """
    Input is an empty string, output is the current data and time.
    Always use this tool before generating a query if there is any time or date in the given question.
    """

    @catch_exceptions
    def _run(
        self,
        tool_input: str = "",  # noqa: ARG002
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        current_datetime = datetime.datetime.now()
        return f"Current Date and Time: {str(current_datetime)}"

    async def _arun(
        self,
        tool_input: str = "",
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("GetCurrentTimeTool does not support async")


class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name = "sql_db_query"
    description = """
    Input: SQL query.
    Output: Result from the database or an error message if the query is incorrect.
    If an error occurs, rewrite the query and retry.
    Use this tool to execute SQL queries.
    """

    @catch_exceptions
    def _run(
        self,
        query: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        try:
            run_result = self.db.run_sql(query)[0]
        except SQLAlchemyError as e:
            """Format the error message"""
            run_result = f"Error: {e}"
        return run_result

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

    @catch_exceptions
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


class ColumnEntityChecker(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting sample rows for the given column."""

    name = "db_column_entity_checker"
    description = """
    Input: Column name and its corresponding table, and an entity.
    Output: cell-values found in the column similar to the given entity.
    Use this tool to get cell values similar to the given entity in the given column.

    Example Input: table1 -> column2, entity
    """

    def find_similar_strings(
        self, input_list: List[tuple], target_string: str, threshold=0.6
    ):
        similar_strings = []
        for item in input_list:
            similarity = difflib.SequenceMatcher(
                None, str(item[0]).strip(), target_string
            ).ratio()
            if similarity >= threshold:
                similar_strings.append((str(item[0]).strip(), similarity))
        similar_strings.sort(key=lambda x: x[1], reverse=True)
        return similar_strings[:25]

    @catch_exceptions
    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        schema, entity = tool_input.split(",")
        table_name, column_name = schema.split("->")
        query = f"SELECT DISTINCT {column_name} FROM {table_name}"  # noqa: S608
        results = self.db.run_sql(query)[1]["result"]
        results = self.find_similar_strings(results, entity)
        similar_items = "Similar items:\n"
        for item in results:
            similar_items += f"{item[0]}\n"
        return similar_items

    async def _arun(
        self,
        tool_input: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("ColumnsSampleRowsTool does not support async")


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

    @catch_exceptions
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

    @catch_exceptions
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
                    if found:
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
    Input: Number of required Question/SQL pairs.
    Output: List of similar Question/SQL pairs related to the given question.
    Use this tool to fetch previously asked Question/SQL pairs as examples for improving SQL query generation.
    For complex questions, request more examples to gain a better understanding of tables and columns and the SQL keywords to use.
    If the given question is very similar to one of the retrieved examples, it is recommended to use the same SQL query and modify it slightly to fit the given question.
    Always use this tool first and before any other tool!
    """  # noqa: E501
    few_shot_examples: List[dict]

    @catch_exceptions
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
    context: List[dict] | None = Field(exclude=True, default=None)
    few_shot_examples: List[dict] | None = Field(exclude=True, default=None)
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
        tools = []
        query_sql_db_tool = QuerySQLDataBaseTool(db=self.db, context=self.context)
        tools.append(query_sql_db_tool)
        get_current_datetime = GetCurrentTimeTool(db=self.db, context=self.context)
        tools.append(get_current_datetime)
        tables_sql_db_tool = TablesSQLDatabaseTool(
            db=self.db, context=self.context, db_scan=self.db_scan
        )
        tools.append(tables_sql_db_tool)
        schema_sql_db_tool = SchemaSQLDatabaseTool(
            db=self.db, context=self.context, db_scan=self.db_scan
        )
        tools.append(schema_sql_db_tool)
        info_relevant_tool = InfoRelevantColumns(
            db=self.db, context=self.context, db_scan=self.db_scan
        )
        tools.append(info_relevant_tool)
        column_sample_tool = ColumnEntityChecker(db=self.db, context=self.context)
        tools.append(column_sample_tool)
        if self.few_shot_examples is not None:
            get_fewshot_examples_tool = GetFewShotExamples(
                db=self.db,
                context=self.context,
                few_shot_examples=self.few_shot_examples,
            )
            tools.append(get_fewshot_examples_tool)
        return tools


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
        top_k: int = 13,
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
        start_time = time.time()
        context_store = self.system.instance(ContextStore)
        storage = self.system.instance(DB)
        repository = DBScannerRepository(storage)
        db_scan = repository.get_all_tables_by_db(db_alias=database_connection.alias)
        if not db_scan:
            raise ValueError("No scanned tables found for database")
        few_shot_examples = context_store.retrieve_context_for_question(
            user_question, number_of_samples=self.max_number_of_examples
        )
        if few_shot_examples is not None:
            new_fewshot_examples = self.remove_duplicate_examples(few_shot_examples)
            number_of_samples = len(new_fewshot_examples)
        else:
            new_fewshot_examples = None
            number_of_samples = 0
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
            max_examples=number_of_samples,
        )
        agent_executor.return_intermediate_steps = True
        agent_executor.handle_parsing_errors = True
        with get_openai_callback() as cb:
            result = agent_executor({"input": user_question.question})
        intermediate_steps = []
        sql_query_list = []
        for step in result["intermediate_steps"]:
            action = step[0]
            if type(action) == AgentAction and action.tool == "sql_db_query":
                sql_query_list.append(action.tool_input)

            intermediate_steps.append(str(step))
        exec_time = time.time() - start_time
        logger.info(
            f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)} time: {str(exec_time)}"
        )
        response = NLQueryResponse(
            nl_question_id=user_question.id,
            nl_response=result["output"],
            intermediate_steps=intermediate_steps,
            exec_time=exec_time,
            total_tokens=cb.total_tokens,
            total_cost=cb.total_cost,
            sql_query=sql_query_list[-1] if len(sql_query_list) > 0 else "",
        )
        return self.create_sql_query_status(self.database, response.sql_query, response)
