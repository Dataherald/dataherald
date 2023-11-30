import datetime
import difflib
import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, List

import numpy as np
import openai
import pandas as pd
import sqlalchemy
from bson.objectid import ObjectId
from google.api_core.exceptions import GoogleAPIError
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
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import AgentAction
from langchain.tools.base import BaseTool
from overrides import override
from pydantic import BaseModel, Field
from sqlalchemy import MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.db_scanner.models.types import TableDescription, TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_database.models.types import (
    DatabaseConnection,
)
from dataherald.sql_generator import EngineTimeOutORItemLimitError, SQLGenerator
from dataherald.types import Question, Response
from dataherald.utils.agent_prompts import (
    AGENT_PREFIX,
    FORMAT_INSTRUCTIONS,
    PLAN_BASE,
    PLAN_WITH_FEWSHOT_EXAMPLES,
    PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS,
    PLAN_WITH_INSTRUCTIONS,
    SUFFIX_WITH_FEW_SHOT_SAMPLES,
    SUFFIX_WITHOUT_FEW_SHOT_SAMPLES,
)

logger = logging.getLogger(__name__)


TOP_K = int(os.getenv("UPPER_LIMIT_QUERY_RETURN_ROWS", "50"))
EMBEDDING_MODEL = "text-embedding-ada-002"


def catch_exceptions():  # noqa: C901
    def decorator(fn: Callable[[str], str]) -> Callable[[str], str]:  # noqa: C901
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: PLR0911
            try:
                return fn(*args, **kwargs)
            except openai.AuthenticationError as e:
                # Handle authentication error here
                return f"OpenAI API authentication error: {e}"
            except openai.RateLimitError as e:
                # Handle API error here, e.g. retry or log
                return f"OpenAI API request exceeded rate limit: {e}"
            except openai.BadRequestError as e:
                # Handle connection error here
                return f"OpenAI API request timed out: {e}"
            except openai.APIResponseValidationError as e:
                # Handle rate limit error (we recommend using exponential backoff)
                return f"OpenAI API response is invalid: {e}"
            except openai.OpenAIError as e:
                # Handle timeout error (we recommend using exponential backoff)
                return f"OpenAI API returned an error: {e}"
            except GoogleAPIError as e:
                return f"Google API returned an error: {e}"
            except SQLAlchemyError as e:
                return f"Error: {e}"

        return wrapper

    return decorator


# Classes needed for tools
class BaseSQLDatabaseTool(BaseModel):
    """Base tool for interacting with the SQL database and the context information."""

    db: SQLDatabase = Field(exclude=True)
    context: List[dict] | None = Field(exclude=True, default=None)

    class Config(BaseTool.Config):
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True
        extra = "allow"


class SystemTime(BaseSQLDatabaseTool, BaseTool):
    """Tool for finding the current data and time."""

    name = "system_time"
    description = """
    Input is an empty string, output is the current data and time.
    Always use this tool before generating a query if there is any time or date in the given question.
    """

    @catch_exceptions()
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

    @catch_exceptions()
    def _run(
        self,
        query: str,
        top_k: int = TOP_K,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        if "```sql" in query:
            logger.info("**** Removing markdown formatting from the query\n")
            query = query.replace("```sql", "").replace("```", "")
            logger.info(f"**** Query after removing markdown formatting: {query}\n")
        return self.db.run_sql(query, top_k=top_k)[0]

    async def _arun(
        self,
        query: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("QuerySQLDataBaseTool does not support async")


class GetUserInstructions(BaseSQLDatabaseTool, BaseTool):
    """Tool for retrieving the instructions from the user"""

    name = "get_admin_instructions"
    description = """
    Input: is an empty string.
    Output: Database admin instructions before generating the SQL query.
    The generated SQL query MUST follow the admin instructions even it contradicts with the given question.
    """
    instructions: List[dict]

    @catch_exceptions()
    def _run(
        self,
        tool_input: str = "",  # noqa: ARG002
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        response = "Admin: All of the generated SQL queries must follow the below instructions:\n"
        for instruction in self.instructions:
            response += f"{instruction['instruction']}\n"
        return response

    async def _arun(
        self,
        tool_input: str = "",  # noqa: ARG002
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("GetUserInstructions does not support async")


class TablesSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool which takes in the given question and returns a list of tables with their relevance score to the question"""

    name = "db_tables_with_relevance_scores"
    description = """
    Input: Given question.
    Output: Comma-separated list of tables with their relevance scores, indicating their relevance to the question.
    Use this tool to identify the relevant tables for the given question.
    """
    db_scan: List[TableDescription]
    embedding: OpenAIEmbeddings

    def get_embedding(
        self,
        text: str,
    ) -> List[float]:
        text = text.replace("\n", " ")
        return self.embedding.embed_query(text)

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        return round(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), 4)

    @catch_exceptions()
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
        raise NotImplementedError("TablesSQLDatabaseTool does not support async")


class ColumnEntityChecker(BaseSQLDatabaseTool, BaseTool):
    """Tool for checking the existance of an entity inside a column."""

    name = "db_column_entity_checker"
    description = """
    Input: Column name and its corresponding table, and an entity.
    Output: cell-values found in the column similar to the given entity.
    Use this tool to get cell values similar to the given entity in the given column.

    Example Input: table1 -> column2, entity
    """

    def find_similar_strings(
        self, input_list: List[tuple], target_string: str, threshold=0.4
    ):
        similar_strings = []
        for item in input_list:
            similarity = difflib.SequenceMatcher(
                None, str(item[0]).strip().lower(), target_string.lower()
            ).ratio()
            if similarity >= threshold:
                similar_strings.append((str(item[0]).strip(), similarity))
        similar_strings.sort(key=lambda x: x[1], reverse=True)
        return similar_strings[:25]

    @catch_exceptions()
    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        try:
            schema, entity = tool_input.split(",")
            table_name, column_name = schema.split("->")
        except ValueError:
            return "Invalid input format, use following format: table_name -> column_name, entity (entity should be a string without ',')"
        search_pattern = f"%{entity.strip().lower()}%"
        meta = MetaData(bind=self.db.engine)
        table = sqlalchemy.Table(table_name.strip(), meta, autoload=True)
        try:
            search_query = sqlalchemy.select(
                [func.distinct(table.c[column_name.strip()])]
            ).where(func.lower(table.c[column_name.strip()]).like(search_pattern))
            search_results = self.db.engine.execute(search_query).fetchall()
            search_results = search_results[:25]
        except SQLAlchemyError:
            search_results = []
        distinct_query = sqlalchemy.select(
            [func.distinct(table.c[column_name.strip()])]
        )
        results = self.db.engine.execute(distinct_query).fetchall()
        results = self.find_similar_strings(results, entity)
        similar_items = "Similar items:\n"
        already_added = {}
        for item in results:
            similar_items += f"{item[0]}\n"
            already_added[item[0]] = True
        if len(search_results) > 0:
            for item in search_results:
                if item[0] not in already_added:
                    similar_items += f"{item[0]}\n"
        return similar_items

    async def _arun(
        self,
        tool_input: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("ColumnEntityChecker does not support async")


class SchemaSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting schema of relevant tables."""

    name = "db_relevant_tables_schema"
    description = """
    Input: Comma-separated list of tables.
    Output: Schema of the specified tables.
    Use this tool to discover all columns of the relevant tables and identify potentially relevant columns.

    Example Input: table1, table2, table3
    """
    db_scan: List[TableDescription]

    @catch_exceptions()
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
                if table.description is not None:
                    tables_schema += "Table description: " + table.description + "\n"
        if tables_schema == "":
            tables_schema += "Tables not found in the database"
        return tables_schema

    async def _arun(
        self,
        table_name: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("SchemaSQLDatabaseTool does not support async")


class InfoRelevantColumns(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting more information for potentially relevant columns"""

    name = "db_relevant_columns_info"
    description = """
    Input: Comma-separated list of potentially relevant columns with their corresponding table.
    Output: Information about the values inside the columns and their descriptions.
    Use this tool to gather details about potentially relevant columns. then, filter them, and identify the relevant ones.

    Example Input: table1 -> column1, table1 -> column2, table2 -> column1
    """
    db_scan: List[TableDescription]

    @catch_exceptions()
    def _run(
        self,
        column_names: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the column level information."""
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

    @catch_exceptions()
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
    instructions: List[dict] | None = Field(exclude=True, default=None)
    db_scan: List[TableDescription] = Field(exclude=True)
    embedding: OpenAIEmbeddings = Field(exclude=True)

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
        if self.instructions is not None:
            tools.append(
                GetUserInstructions(
                    db=self.db, context=self.context, instructions=self.instructions
                )
            )
        get_current_datetime = SystemTime(db=self.db, context=self.context)
        tools.append(get_current_datetime)
        tables_sql_db_tool = TablesSQLDatabaseTool(
            db=self.db,
            context=self.context,
            db_scan=self.db_scan,
            embedding=self.embedding,
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

    max_number_of_examples: int = 5  # maximum number of question/SQL pairs
    llm: Any = None

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
        number_of_instructions: int = 1,
        max_iterations: int
        | None = int(os.getenv("AGENT_MAX_ITERATIONS", "20")),  # noqa: B008
        max_execution_time: float | None = None,
        early_stopping_method: str = "force",
        verbose: bool = False,
        agent_executor_kwargs: Dict[str, Any] | None = None,
        **kwargs: Dict[str, Any],
    ) -> AgentExecutor:
        """Construct an SQL agent from an LLM and tools."""
        tools = toolkit.get_tools()
        if max_examples > 0 and number_of_instructions > 0:
            plan = PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS
            suffix = SUFFIX_WITH_FEW_SHOT_SAMPLES
        elif max_examples > 0:
            plan = PLAN_WITH_FEWSHOT_EXAMPLES
            suffix = SUFFIX_WITH_FEW_SHOT_SAMPLES
        elif number_of_instructions > 0:
            plan = PLAN_WITH_INSTRUCTIONS
            suffix = SUFFIX_WITHOUT_FEW_SHOT_SAMPLES
        else:
            plan = PLAN_BASE
            suffix = SUFFIX_WITHOUT_FEW_SHOT_SAMPLES
        plan = plan.format(
            dialect=toolkit.dialect,
            max_examples=max_examples,
        )
        prefix = prefix.format(
            dialect=toolkit.dialect, max_examples=max_examples, agent_plan=plan
        )
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
    def generate_response(
        self,
        user_question: Question,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
        generate_csv: bool = False,
    ) -> Response:
        context_store = self.system.instance(ContextStore)
        storage = self.system.instance(DB)
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=os.getenv("LLM_MODEL", "gpt-4-1106-preview"),
        )
        repository = TableDescriptionRepository(storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": ObjectId(database_connection.id),
                "status": TableDescriptionStatus.SYNCHRONIZED.value,
            }
        )
        if not db_scan:
            raise ValueError("No scanned tables found for database")
        few_shot_examples, instructions = context_store.retrieve_context_for_question(
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
            instructions=instructions,
            db_scan=db_scan,
            embedding=OpenAIEmbeddings(
                openai_api_key=database_connection.decrypt_api_key(),
                model=EMBEDDING_MODEL,
            ),
        )
        agent_executor = self.create_sql_agent(
            toolkit=toolkit,
            verbose=True,
            max_examples=number_of_samples,
            number_of_instructions=len(instructions) if instructions is not None else 0,
            max_execution_time=os.getenv("DH_ENGINE_TIMEOUT", None),
        )
        agent_executor.return_intermediate_steps = True
        agent_executor.handle_parsing_errors = True
        with get_openai_callback() as cb:
            try:
                result = agent_executor({"input": user_question.question})
                result = self.check_for_time_out_or_tool_limit(result)
            except SQLInjectionError as e:
                raise SQLInjectionError(e) from e
            except EngineTimeOutORItemLimitError as e:
                raise EngineTimeOutORItemLimitError(e) from e
            except Exception as e:
                return Response(
                    question_id=user_question.id,
                    total_tokens=cb.total_tokens,
                    total_cost=cb.total_cost,
                    sql_query="",
                    sql_generation_status="INVALID",
                    sql_query_result=None,
                    error_message=str(e),
                )
        sql_query_list = []
        for step in result["intermediate_steps"]:
            action = step[0]
            if type(action) == AgentAction and action.tool == "sql_db_query":
                query = self.format_sql_query(action.tool_input)
                if "```sql" in query:
                    logger.info("**** Removing markdown formatting from the query\n")
                    query = query.replace("```sql", "").replace("```", "")
                    logger.info(
                        f"**** Query after removing markdown formatting: {query}\n"
                    )
                sql_query_list.append(query)
        intermediate_steps = self.format_intermediate_representations(
            result["intermediate_steps"]
        )
        logger.info(f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)}")
        response = Response(
            question_id=user_question.id,
            response=result["output"],
            intermediate_steps=intermediate_steps,
            total_tokens=cb.total_tokens,
            total_cost=cb.total_cost,
            sql_query=sql_query_list[-1] if len(sql_query_list) > 0 else "",
        )
        return self.create_sql_query_status(
            self.database,
            response.sql_query,
            response,
            top_k=TOP_K,
            generate_csv=generate_csv,
            database_connection=database_connection,
        )
