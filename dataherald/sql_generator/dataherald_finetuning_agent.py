import datetime
import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, List, Type

import openai
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
from langchain.schema import AgentAction
from langchain.tools.base import BaseTool
from overrides import override
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

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
    FINETUNING_AGENT_PREFIX,
    FINETUNING_AGENT_SUFFIX,
    FINETUNING_SYSTEM_INFORMATION,
    FORMAT_INSTRUCTIONS,
)

logger = logging.getLogger(__name__)

TOP_K = int(os.getenv("UPPER_LIMIT_QUERY_RETURN_ROWS", "50"))


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


class SQLInput(BaseModel):
    sql_query: str = Field()


class QuestionInput(BaseModel):
    question: str = Field()


class BaseSQLDatabaseTool(BaseModel):
    """Base tool for interacting with the SQL database and the context information."""

    db: SQLDatabase = Field(exclude=True)

    class Config(BaseTool.Config):
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True
        extra = "allow"


class SystemTime(BaseSQLDatabaseTool, BaseTool):
    """Tool for finding the current data and time."""

    name = "system_time"
    description = """
    Use this tool to replace current_time and current_date in SQL queries with the actual current time and date.
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
        raise NotImplementedError("SystemTime tool does not support async")


class TablesSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool which takes in the given question and returns a list of tables with their relevance score to the question"""

    name = "get_db_table_names"
    description = """
    Use this tool to get the list of tables in the database.
    """
    db_scan: List[TableDescription]

    @catch_exceptions()
    def _run(
        self,
        input: str,  # noqa: ARG002
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Use the concatenation of table name, columns names, and the description of the table as the table representation"""
        tables = []
        for table in self.db_scan:
            tables.append(table.table_name)
        return f"Tables in the database: {','.join(tables)}"

    async def _arun(
        self,
        input: str = "",
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("TablesSQLDatabaseTool does not support async")


class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name = "sql_db_query"
    description = """
    Use this tool to execute the SQL query on the database, and return the results.
    """
    args_schema: Type[BaseModel] = SQLInput

    @catch_exceptions()
    def _run(
        self,
        query: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        if "```sql" in query:
            logger.info("**** Removing markdown formatting from the query\n")
            query = query.replace("```sql", "").replace("```", "")
            logger.info(f"**** Query after removing markdown formatting: {query}\n")
        return self.db.run_sql(query, top_k=TOP_K)[0]

    async def _arun(
        self,
        query: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("QuerySQLDataBaseTool does not support async")


class GenerateSQL(BaseSQLDatabaseTool, BaseTool):
    """Tool for generating SQL queries."""

    name = "generate_sql"
    description = """
    Use this tool to generate SQL queries.
    Pass the user question as the input to the tool.
    """
    args_schema: Type[BaseModel] = QuestionInput
    db_scan: List[TableDescription]
    instructions: List[dict] | None = Field(exclude=True, default=None)
    api_key: str = Field(exclude=True)

    def format_columns(self, table: TableDescription, top_k: int = 100) -> str:
        """
        format_columns formats the columns.

        Args:
            table: The table to format.
            top_k: The number of categories to show.

        Returns:
            The formatted columns in string format.
        """
        columns_information = ""
        for column in table.columns:
            name = column.name
            is_primary_key = column.is_primary_key
            if is_primary_key:
                primary_key_text = (
                    f"this column is a primary key of the table {table.table_name},"
                )
            else:
                primary_key_text = ""
            foreign_key = column.foreign_key
            if foreign_key:
                foreign_key_text = (
                    f"this column has a foreign key to the table {foreign_key},"
                )
            else:
                foreign_key_text = ""
            categories = column.categories
            if categories:
                if len(categories) <= top_k:
                    categories_text = f"Categories: {categories},"
                else:
                    categories_text = ""
            else:
                categories_text = ""
            if primary_key_text or foreign_key_text or categories_text:
                columns_information += (
                    f"{name}: {primary_key_text}{foreign_key_text}{categories_text}\n"
                )
        return columns_information

    def format_database_schema(
        self, db_scan: List[TableDescription], top_k: int = 100
    ) -> str:
        """
        format_database_schema formats the database schema.

        Args:
            db_scan: The database schema.

        Returns:
            The formatted database schema in string format.
        """
        schema_of_database = ""
        for table in db_scan:
            tables_schema = table.table_schema
            schema_of_database += f"{tables_schema}\n"
            schema_of_database += "# Categorical Columns:\n"
            columns_information = self.format_columns(table, top_k)
            schema_of_database += columns_information
            sample_rows = table.examples
            schema_of_database += "# Sample rows:\n"
            for item in sample_rows:
                for key, value in item.items():
                    schema_of_database += f"{key}: {value}, "
                schema_of_database += "\n"
            schema_of_database += "\n\n"
        return schema_of_database

    @catch_exceptions()
    def _run(
        self,
        question: str = "",
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        system_prompt = FINETUNING_SYSTEM_INFORMATION + self.format_database_schema(
            self.db_scan
        )
        if self.instructions:
            user_prompt = "Database administrator rules that should be followed:\n"
            for index, instruction in enumerate(self.instructions):
                user_prompt += f"{index+1}) {instruction['instruction']}\n"
            user_prompt += "\n\n"
            user_prompt += "User Question: " + question
        else:
            user_prompt = "User Question: " + question
        response = openai.ChatCompletion.create(
            model=os.getenv(
                "FINETUNED_MODEL", "gpt-4-1106-preview"
            ),  # gpt-4-1106-preview is included only for avoiding the error
            api_key=self.api_key,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.choices[0]["message"]["content"]

    async def _arun(
        self,
        tool_input: str = "",
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("GenerateSQL tool does not support async")


class SchemaSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting schema of relevant tables."""

    name = "db_schema"
    description = """
    Input: Comma-separated list of tables.
    Output: Schema of the specified tables.
    Use this tool to find the schema of the specified tables, if you are unsure about the schema of the tables when editing the SQL query.
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


class SQLDatabaseToolkit(BaseToolkit):
    """Dataherald toolkit"""

    db: SQLDatabase = Field(exclude=True)
    instructions: List[dict] | None = Field(exclude=True, default=None)
    db_scan: List[TableDescription] = Field(exclude=True)
    api_key: str = Field(exclude=True)

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
        tools.append(SystemTime(db=self.db))
        tools.append(QuerySQLDataBaseTool(db=self.db))
        tools.append(
            GenerateSQL(
                db=self.db,
                db_scan=self.db_scan,
                instructions=self.instructions,
                api_key=self.api_key,
            )
        )
        tools.append(SchemaSQLDatabaseTool(db=self.db, db_scan=self.db_scan))
        tools.append(TablesSQLDatabaseTool(db=self.db, db_scan=self.db_scan))
        return tools


class DataheraldFinetuningAgent(SQLGenerator):
    """
    DataheraldFinetuningAgent is a class that uses a Finetuning model to generate SQL queries.
    """

    llm: Any = None

    def create_sql_agent(
        self,
        toolkit: SQLDatabaseToolkit,
        callback_manager: BaseCallbackManager | None = None,
        prefix: str = FINETUNING_AGENT_PREFIX,
        suffix: str = FINETUNING_AGENT_SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: List[str] | None = None,
        max_iterations: int
        | None = int(os.getenv("AGENT_MAX_ITERATIONS", "20")),  # noqa: B008
        max_execution_time: float | None = None,
        early_stopping_method: str = "force",
        verbose: bool = False,
        agent_executor_kwargs: Dict[str, Any] | None = None,
        **kwargs: Dict[str, Any],
    ) -> AgentExecutor:
        tools = toolkit.get_tools()
        admin_instructions = ""
        for index, instruction in enumerate(toolkit.instructions):
            admin_instructions += f"{index+1}) {instruction['instruction']}\n"
        prefix = prefix.format(
            dialect=toolkit.dialect, admin_instructions=admin_instructions
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
        context: List[dict] = None,  # noqa: ARG002
        generate_csv: bool = False,
    ) -> Response:
        """
        generate_response generates a response to a user question using a Finetuning model.

        Args:
            user_question (Question): The user question to generate a response to.
            database_connection (DatabaseConnection): The database connection to use.
            context (List[dict], optional): The context to use. Defaults to None.
            generate_csv (bool, optional): Whether to generate a CSV. Defaults to False.

        Returns:
            Response: The response to the user question.
        """
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
        _, instructions = context_store.retrieve_context_for_question(
            user_question, number_of_samples=1
        )

        self.database = SQLDatabase.get_sql_engine(database_connection)
        toolkit = SQLDatabaseToolkit(
            db=self.database,
            instructions=instructions,
            db_scan=db_scan,
            api_key=database_connection.decrypt_api_key(),
        )
        agent_executor = self.create_sql_agent(
            toolkit=toolkit,
            verbose=True,
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
