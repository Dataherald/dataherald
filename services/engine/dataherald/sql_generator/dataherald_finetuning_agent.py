import datetime
import logging
import os
from functools import wraps
from queue import Queue
from threading import Thread
from typing import Any, Callable, Dict, List, Type

import numpy as np
import openai
import pandas as pd
from google.api_core.exceptions import GoogleAPIError
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.chains.llm import LLMChain
from langchain.tools.base import BaseTool
from langchain_community.callbacks import get_openai_callback
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from openai import OpenAI
from overrides import override
from pydantic import BaseModel, Field
from sql_metadata import Parser
from sqlalchemy.exc import SQLAlchemyError

from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.db_scanner.models.types import TableDescription, TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.finetuning.openai_finetuning import OpenAIFineTuning
from dataherald.repositories.finetunings import FinetuningsRepository
from dataherald.repositories.sql_generations import (
    SQLGenerationRepository,
)
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_database.models.types import (
    DatabaseConnection,
)
from dataherald.sql_generator import EngineTimeOutORItemLimitError, SQLGenerator
from dataherald.types import FineTuningStatus, Prompt, SQLGeneration
from dataherald.utils.agent_prompts import (
    ERROR_PARSING_MESSAGE,
    FINETUNING_AGENT_PREFIX,
    FINETUNING_AGENT_PREFIX_FINETUNING_ONLY,
    FINETUNING_AGENT_SUFFIX,
    FINETUNING_SYSTEM_INFORMATION,
    FORMAT_INSTRUCTIONS,
)
from dataherald.utils.models_context_window import OPENAI_FINETUNING_MODELS_WINDOW_SIZES
from dataherald.utils.timeout_utils import run_with_timeout

logger = logging.getLogger(__name__)


TOP_K = SQLGenerator.get_upper_bound_limit()
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL","text-embedding-3-large")
TOP_TABLES = 20


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

    name = "DbTablesWithRelevanceScores"
    description = """
    Input: Given question.
    Output: Comma-separated list of tables with their relevance scores, indicating their relevance to the question.
    Use this tool to identify the relevant tables for the given question.
    """
    db_scan: List[TableDescription]
    embedding: OpenAIEmbeddings
    few_shot_examples: List[dict] | None = Field(exclude=True, default=None)

    def get_embedding(
        self,
        text: str,
    ) -> List[float]:
        text = text.replace("\n", " ")
        return self.embedding.embed_query(text)

    def get_docs_embedding(
        self,
        docs: List[str],
    ) -> List[List[float]]:
        return self.embedding.embed_documents(docs)

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        return round(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), 4)

    def similar_tables_based_on_few_shot_examples(self, df: pd.DataFrame) -> List[str]:
        most_similar_tables = set()
        if self.few_shot_examples is not None:
            for example in self.few_shot_examples:
                try:
                    tables = Parser(example["sql"]).tables
                except Exception as e:
                    logger.error(f"Error parsing SQL: {str(e)}")
                for table in tables:
                    found_tables = df[df.table_name == table]
                    for _, row in found_tables.iterrows():
                        most_similar_tables.add((row["schema_name"], row["table_name"]))
            df.drop(
                df[
                    df.table_name.isin([table[1] for table in most_similar_tables])
                ].index,
                inplace=True,
            )
        return most_similar_tables

    @catch_exceptions()
    def _run(  # noqa: PLR0912
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
                if column.description:
                    col_rep += f"{column.name}: {column.description}, "
                else:
                    col_rep += f"{column.name}, "
            if table.description:
                table_rep = f"Table {table.table_name} contain columns: [{col_rep}], this tables has: {table.description}"
            else:
                table_rep = f"Table {table.table_name} contain columns: [{col_rep}]"
            table_representations.append(
                [table.schema_name, table.table_name, table_rep]
            )
        df = pd.DataFrame(
            table_representations,
            columns=["schema_name", "table_name", "table_representation"],
        )
        df["table_embedding"] = self.get_docs_embedding(df.table_representation)
        df["similarities"] = df.table_embedding.apply(
            lambda x: self.cosine_similarity(x, question_embedding)
        )
        df = df.sort_values(by="similarities", ascending=True)
        df = df.tail(TOP_TABLES)
        most_similar_tables = self.similar_tables_based_on_few_shot_examples(df)
        table_relevance = ""
        for _, row in df.iterrows():
            if row["schema_name"] is not None:
                table_name = row["schema_name"] + "." + row["table_name"]
            else:
                table_name = row["table_name"]
            table_relevance += (
                f'Table: `{table_name}`, relevance score: {row["similarities"]}\n'
            )
        if len(most_similar_tables) > 0:
            for table in most_similar_tables:
                if table[0] is not None:
                    table_name = table[0] + "." + table[1]
                else:
                    table_name = table[1]
                table_relevance += f"Table: `{table_name}`, relevance score: {max(df['similarities'])}\n"
        return table_relevance

    async def _arun(
        self,
        user_question: str = "",
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        raise NotImplementedError("TablesSQLDatabaseTool does not support async")


class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name = "SqlDbQuery"
    description = """
    Input: A SQL query between ```sql and ``` tags.
    Output: Result from the database or an error message if the query is incorrect.
    Use this tool to execute the SQL query on the database, and return the results.
    Add newline after both ```sql and ``` tags.
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

        try:
            return run_with_timeout(
                self.db.run_sql,
                args=(query,),
                kwargs={"top_k": TOP_K},
                timeout_duration=int(os.getenv("SQL_EXECUTION_TIMEOUT", "60")),
            )[0]
        except TimeoutError:
            return "SQL query execution time exceeded, proceed without query execution"

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
    embedding: OpenAIEmbeddings = Field(exclude=True)

    @catch_exceptions()
    def _run(
        self,
        question: str = "",
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        table_representations = []
        for table in self.db_scan:
            table_representations.append(
                self.openai_fine_tuning.create_table_representation(table)
            )
        table_embeddings = self.embedding.embed_documents(table_representations)
        system_prompt = (
            FINETUNING_SYSTEM_INFORMATION
            + self.openai_fine_tuning.format_dataset(
                self.db_scan,
                table_embeddings,
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
        returned_sql = response.choices[0].message.content
        return f"```sql\n{returned_sql}```"

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
    def _run(  # noqa: C901
        self,
        table_names: str,
        run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        table_names_list = table_names.split(", ")
        processed_table_names = []
        for table in table_names_list:
            formatted_table = replace_unprocessable_characters(table)
            if "." in formatted_table:
                processed_table_names.append(formatted_table.split(".")[1])
            else:
                processed_table_names.append(formatted_table)
        tables_schema = ""
        for table in self.db_scan:
            if table.table_name in processed_table_names:
                tables_schema += "```sql\n"
                tables_schema += table.table_schema + "\n"
                descriptions = []
                if table.description is not None:
                    if table.schema_name:
                        table_name = f"{table.schema_name}.{table.table_name}"
                    else:
                        table_name = table.table_name
                    descriptions.append(f"Table `{table_name}`: {table.description}\n")
                    for column in table.columns:
                        if column.description is not None:
                            descriptions.append(
                                f"Column `{column.name}`: {column.description}\n"
                            )
                if len(descriptions) > 0:
                    tables_schema += f"/*\n{''.join(descriptions)}*/\n"
                tables_schema += "```\n"
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
    embedding: OpenAIEmbeddings = Field(exclude=True)
    few_shot_examples: List[dict] | None = Field(exclude=True, default=None)

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
            tools.append(
                TablesSQLDatabaseTool(
                    db=self.db,
                    db_scan=self.db_scan,
                    embedding=self.embedding,
                    few_shot_examples=self.few_shot_examples,
                )
            )
        tools.append(QuerySQLDataBaseTool(db=self.db))
        tools.append(
            GenerateSQL(
                db=self.db,
                db_scan=self.db_scan,
                api_key=self.api_key,
                finetuning_model_id=self.finetuning_model_id,
                model_name=self.model_name,
                openai_fine_tuning=self.openai_fine_tuning,
                embedding=self.embedding,
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
        max_iterations: int | None = int(
            os.getenv("AGENT_MAX_ITERATIONS", "12")
        ),  # noqa: B008
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
        metadata: dict = None,
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
        db_scan = SQLGenerator.filter_tables_by_schema(
            db_scan=db_scan, prompt=user_prompt
        )
        few_shot_examples, instructions = context_store.retrieve_context_for_question(
            user_prompt, number_of_samples=5
        )
        finetunings_repository = FinetuningsRepository(storage)
        finetuning = finetunings_repository.find_by_id(self.finetuning_id)
        openai_fine_tuning = OpenAIFineTuning(self.system, storage, finetuning)
        finetuning = openai_fine_tuning.retrieve_finetuning_job()
        if finetuning.status != FineTuningStatus.SUCCEEDED.value:
            raise FinetuningNotAvailableError(
                f"Finetuning({self.finetuning_id}) has the status {finetuning.status}."
                f"Finetuning should have the status {FineTuningStatus.SUCCEEDED.value} to generate SQL queries."
            )
        self.database = SQLDatabase.get_sql_engine(database_connection)
        if self.system.settings["azure_api_key"] is not None:
            embedding = AzureOpenAIEmbeddings(
                openai_api_key=database_connection.decrypt_api_key(),
                model=EMBEDDING_MODEL,
            )
        else:
            embedding = OpenAIEmbeddings(
                openai_api_key=database_connection.decrypt_api_key(),
                model=EMBEDDING_MODEL,
            )
        toolkit = SQLDatabaseToolkit(
            db=self.database,
            instructions=instructions,
            few_shot_examples=few_shot_examples,
            db_scan=db_scan,
            api_key=database_connection.decrypt_api_key(),
            finetuning_model_id=finetuning.model_id,
            use_finetuned_model_only=self.use_fintuned_model_only,
            model_name=finetuning.base_llm.model_name,
            openai_fine_tuning=openai_fine_tuning,
            embedding=embedding,
        )
        agent_executor = self.create_sql_agent(
            toolkit=toolkit,
            verbose=True,
            max_execution_time=int(os.environ.get("DH_ENGINE_TIMEOUT", 150)),
        )
        agent_executor.return_intermediate_steps = True
        agent_executor.handle_parsing_errors = ERROR_PARSING_MESSAGE
        with get_openai_callback() as cb:
            try:
                result = agent_executor.invoke(
                    {"input": user_prompt.text}, {"metadata": metadata}
                )
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
            sql_query = self.extract_query_from_intermediate_steps(
                result["intermediate_steps"]
            )
        logger.info(f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)}")
        response.sql = replace_unprocessable_characters(sql_query)
        response.tokens_used = cb.total_tokens
        response.completed_at = datetime.datetime.now()
        response.intermediate_steps = self.construct_intermediate_steps(
            result["intermediate_steps"], FINETUNING_AGENT_SUFFIX
        )
        return self.create_sql_query_status(
            self.database,
            response.sql,
            response,
        )

    @override
    def stream_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        response: SQLGeneration,
        queue: Queue,
        metadata: dict = None,
    ):
        context_store = self.system.instance(ContextStore)
        storage = self.system.instance(DB)
        sql_generation_repository = SQLGenerationRepository(storage)
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=self.llm_config.llm_name,
            api_base=self.llm_config.api_base,
            streaming=True,
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
        db_scan = SQLGenerator.filter_tables_by_schema(
            db_scan=db_scan, prompt=user_prompt
        )
        _, instructions = context_store.retrieve_context_for_question(
            user_prompt, number_of_samples=1
        )
        finetunings_repository = FinetuningsRepository(storage)
        finetuning = finetunings_repository.find_by_id(self.finetuning_id)
        openai_fine_tuning = OpenAIFineTuning(self.system, storage, finetuning)
        finetuning = openai_fine_tuning.retrieve_finetuning_job()
        if finetuning.status != FineTuningStatus.SUCCEEDED.value:
            raise FinetuningNotAvailableError(
                f"Finetuning({self.finetuning_id}) has the status {finetuning.status}."
                f"Finetuning should have the status {FineTuningStatus.SUCCEEDED.value} to generate SQL queries."
            )
        self.database = SQLDatabase.get_sql_engine(database_connection)
        if self.system.settings["azure_api_key"] is not None:
            embedding = AzureOpenAIEmbeddings(
                openai_api_key=database_connection.decrypt_api_key(),
                model=EMBEDDING_MODEL,
            )
        else:
            embedding = OpenAIEmbeddings(
                openai_api_key=database_connection.decrypt_api_key(),
                model=EMBEDDING_MODEL,
            )
        toolkit = SQLDatabaseToolkit(
            db=self.database,
            instructions=instructions,
            db_scan=db_scan,
            api_key=database_connection.decrypt_api_key(),
            finetuning_model_id=finetuning.model_id,
            use_finetuned_model_only=self.use_fintuned_model_only,
            model_name=finetuning.base_llm.model_name,
            openai_fine_tuning=openai_fine_tuning,
            embedding=embedding,
        )
        agent_executor = self.create_sql_agent(
            toolkit=toolkit,
            verbose=True,
            max_execution_time=int(os.environ.get("DH_ENGINE_TIMEOUT", 150)),
        )
        agent_executor.return_intermediate_steps = True
        agent_executor.handle_parsing_errors = ERROR_PARSING_MESSAGE
        thread = Thread(
            target=self.stream_agent_steps,
            args=(
                user_prompt.text,
                agent_executor,
                response,
                sql_generation_repository,
                queue,
                metadata,
            ),
        )
        thread.start()
