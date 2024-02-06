import datetime
import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, List, Type

import openai
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
from openai import OpenAI
from overrides import override
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.db_scanner.models.types import TableDescription, TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.finetuning.openai_finetuning import OpenAIFineTuning
from dataherald.repositories.finetunings import FinetuningsRepository
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_database.models.types import (
    DatabaseConnection,
)
from dataherald.sql_generator import EngineTimeOutORItemLimitError, SQLGenerator
from dataherald.types import FineTuningStatus, Prompt, SQLGeneration
from dataherald.utils.agent_prompts import (
    FINETUNING_AGENT_PREFIX,
    FINETUNING_AGENT_PREFIX_FINETUNING_ONLY,
    FINETUNING_AGENT_SUFFIX,
    FINETUNING_SYSTEM_INFORMATION,
    FORMAT_INSTRUCTIONS,
)
from dataherald.utils.models_context_window import OPENAI_FINETUNING_MODELS_WINDOW_SIZES

logger = logging.getLogger(__name__)


TOP_K = SQLGenerator.get_upper_bound_limit()


class FinetuningNotAvailableError(Exception):
    """Exception raised when finetuning is not available."""

    pass


def replace_unprocessable_characters(text: str) -> str:
    """Replace unprocessable characters with a space."""
    text = text.strip()
    return text.replace(r"\_", "_")


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

    name = "SystemTime"
    description = """
    Input: None.
    Output: Current date and time.
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

    name = "GetDbTableNames"
    description = """
    Input: None.
    Output: List of tables in the database.
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

    name = "ExecuteQuery"
    description = """
    Input: SQL query.
    Output: Result from the database or an error message if the query is incorrect.
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
        query = replace_unprocessable_characters(query)
        if "```sql" in query:
            query = query.replace("```sql", "").replace("```", "")
        return self.db.run_sql(query, top_k=TOP_K)[0]

    async def _arun(
        self,
        query: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("QuerySQLDataBaseTool does not support async")


class GenerateSQL(BaseSQLDatabaseTool, BaseTool):
    """Tool for generating SQL queries."""

    name = "GenerateSQL"
    description = """
    Input: user question.
    Output: SQL query.
    Use this tool to a generate SQL queries.
    Pass the user question as input to the tool.
    """
    finetuning_model_id: str = Field(exclude=True)
    model_name: str = Field(exclude=True)
    args_schema: Type[BaseModel] = QuestionInput
    db_scan: List[TableDescription]
    api_key: str = Field(exclude=True)
    openai_fine_tuning: OpenAIFineTuning = Field(exclude=True)

    @catch_exceptions()
    def _run(
        self,
        question: str = "",
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        system_prompt = (
            FINETUNING_SYSTEM_INFORMATION
            + self.openai_fine_tuning.format_dataset(
                self.db_scan,
                question,
                OPENAI_FINETUNING_MODELS_WINDOW_SIZES[self.model_name] - 500,
            )
        )
        user_prompt = "User Question: " + question + "\n SQL: "
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.finetuning_model_id,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

    async def _arun(
        self,
        tool_input: str = "",
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("GenerateSQL tool does not support async")


class SchemaSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting schema of relevant tables."""

    name = "DbSchema"
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
        table_names_list = [
            replace_unprocessable_characters(table_name)
            for table_name in table_names_list
        ]
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
    finetuning_model_id: str = Field(exclude=True)
    use_finetuned_model_only: bool = Field(exclude=True, default=None)
    model_name: str = Field(exclude=True)
    openai_fine_tuning: OpenAIFineTuning = Field(exclude=True)

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
        if not self.use_finetuned_model_only:
            tools.append(SystemTime(db=self.db))
            tools.append(SchemaSQLDatabaseTool(db=self.db, db_scan=self.db_scan))
            tools.append(TablesSQLDatabaseTool(db=self.db, db_scan=self.db_scan))
        tools.append(QuerySQLDataBaseTool(db=self.db))
        tools.append(
            GenerateSQL(
                db=self.db,
                db_scan=self.db_scan,
                api_key=self.api_key,
                finetuning_model_id=self.finetuning_model_id,
                model_name=self.model_name,
                openai_fine_tuning=self.openai_fine_tuning,
            )
        )
        return tools


class DataheraldFinetuningAgent(SQLGenerator):
    """
    DataheraldFinetuningAgent is a class that uses a Finetuning model to generate SQL queries.
    """

    llm: Any = None
    finetuning_id: str = Field(exclude=True)
    use_fintuned_model_only: bool = Field(exclude=True, default=False)

    def create_sql_agent(
        self,
        toolkit: SQLDatabaseToolkit,
        callback_manager: BaseCallbackManager | None = None,
        prefix: str = FINETUNING_AGENT_PREFIX,
        suffix: str = FINETUNING_AGENT_SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: List[str] | None = None,
        max_iterations: int
        | None = int(os.getenv("AGENT_MAX_ITERATIONS", "12")),  # noqa: B008
        max_execution_time: float | None = None,
        early_stopping_method: str = "generate",
        verbose: bool = False,
        agent_executor_kwargs: Dict[str, Any] | None = None,
        **kwargs: Dict[str, Any],
    ) -> AgentExecutor:
        tools = toolkit.get_tools()
        admin_instructions = ""
        if toolkit.instructions:
            for index, instruction in enumerate(toolkit.instructions):
                admin_instructions += f"{index+1}) {instruction['instruction']}\n"
        if self.use_fintuned_model_only:
            prefix = FINETUNING_AGENT_PREFIX_FINETUNING_ONLY
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
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,  # noqa: ARG002
    ) -> SQLGeneration:
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
        response = SQLGeneration(
            prompt_id=user_prompt.id,
            created_at=datetime.datetime.now(),
            llm_config=self.llm_config,
            finetuning_id=self.finetuning_id,
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=self.llm_config.llm_name,
            api_base=self.llm_config.api_base,
        )
        repository = TableDescriptionRepository(storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": str(database_connection.id),
                "status": TableDescriptionStatus.SCANNED.value,
            }
        )
        if not db_scan:
            raise ValueError("No scanned tables found for database")
        _, instructions = context_store.retrieve_context_for_question(
            user_prompt, number_of_samples=1
        )
        finetunings_repository = FinetuningsRepository(storage)
        finetuning = finetunings_repository.find_by_id(self.finetuning_id)
        openai_fine_tuning = OpenAIFineTuning(storage, finetuning)
        finetuning = openai_fine_tuning.retrieve_finetuning_job()
        if finetuning.status != FineTuningStatus.SUCCEEDED.value:
            raise FinetuningNotAvailableError(
                f"Finetuning({self.finetuning_id}) has the status {finetuning.status}."
                f"Finetuning should have the status {FineTuningStatus.SUCCEEDED.value} to generate SQL queries."
            )
        self.database = SQLDatabase.get_sql_engine(database_connection)
        toolkit = SQLDatabaseToolkit(
            db=self.database,
            instructions=instructions,
            db_scan=db_scan,
            api_key=database_connection.decrypt_api_key(),
            finetuning_model_id=finetuning.model_id,
            use_finetuned_model_only=self.use_fintuned_model_only,
            model_name=finetuning.base_llm.model_name,
            openai_fine_tuning=openai_fine_tuning,
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
                result = agent_executor({"input": user_prompt.text})
                result = self.check_for_time_out_or_tool_limit(result)
            except SQLInjectionError as e:
                raise SQLInjectionError(e) from e
            except EngineTimeOutORItemLimitError as e:
                raise EngineTimeOutORItemLimitError(e) from e
            except Exception as e:
                return SQLGeneration(
                    prompt_id=user_prompt.id,
                    tokens_used=cb.total_tokens,
                    finetuning_id=self.finetuning_id,
                    completed_at=datetime.datetime.now(),
                    sql="",
                    status="INVALID",
                    error=str(e),
                )
        sql_query = ""
        if "```sql" in result["output"]:
            sql_query = self.remove_markdown(result["output"])
        else:
            for step in result["intermediate_steps"]:
                action = step[0]
                if type(action) == AgentAction and action.tool == "ExecuteQuery":
                    sql_query = self.format_sql_query(action.tool_input)
                    if "```sql" in sql_query:
                        sql_query = self.remove_markdown(sql_query)
        logger.info(f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)}")
        response.sql = replace_unprocessable_characters(sql_query)
        response.tokens_used = cb.total_tokens
        response.completed_at = datetime.datetime.now()
        return self.create_sql_query_status(
            self.database,
            response.sql,
            response,
        )
