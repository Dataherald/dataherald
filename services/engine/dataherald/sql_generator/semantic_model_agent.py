import os
from datetime import datetime
from queue import Queue
from typing import List

from langchain.agents.agent import AgentExecutor
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from overrides import override
from pydantic import BaseModel, Field

from dataherald.db import DB
from dataherald.db_scanner.models.types import TableDescription, TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.sql_database.models.types import (
    DatabaseConnection,
)
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_generator import EngineTimeOutORItemLimitError, SQLGenerator
from dataherald.types import Prompt, SQLGeneration
from dataherald.utils.agent_prompts import SEMANTIC_MODEL_CLASSIFICATION, SEMANTIC_MODEL_SQL_GENERATOR
from dataherald.utils.timeout_utils import run_with_timeout


def replace_unprocessable_characters(text: str) -> str:
    """Replace unprocessable characters with a space."""
    text = text.strip()
    return text.replace(r"\_", "_")

class SQLGenerationOutput(BaseModel):
    reasoning: str = Field(
        description="explanation of the reasoning behind the SQL query"
    )
    sql_query: str = Field(description="SQL query")

class QuestionClassificationOutput(BaseModel):
    reasoning: str = Field(
        description="explanation of the reasoning behind the classification"
    )
    need_feedback: str = Field(description="Yes or No")
    feedback: str = Field(description="feedback on the classification")

class SemanticSQLAgent(SQLGenerator):
    """An experimental agent to use a semantic model for faster and more accurate SQL generation."""
    name = "SemanticSQLAgent"
    description = """ This agent matches the user prompt to a pre-generated semantic model that is
    created from the database schema and query history. In addition to a SQL generation the agent can also
    go back and ask a clarifying question if the prompt is ambiguous.
    """

    db: SQLDatabase = Field(exclude=True)

    def create_semantic_model_agent(
            self,
            ambuguouty_threshold: float
    ) -> AgentExecutor:
        pass


    def execute_sql_query_and_recover(self, database_connection: DatabaseConnection, sql_query: str, max_retries = 3) -> bool:
        query = replace_unprocessable_characters(sql_query)
        if "```sql" in query:
            query = query.replace("```sql", "").replace("```", "")

        database = SQLDatabase.get_sql_engine(database_connection)
        try:
            return run_with_timeout(
                database.run_sql,
                args=(query,),
                kwargs={"top_k": SQLGenerator.get_upper_bound_limit()},
                timeout_duration=int(os.getenv("SQL_EXECUTION_TIMEOUT", "60")),
            )[0]
        except TimeoutError:
            return "SQL query execution time exceeded, proceed without query execution"

    def generate_sql_query(self, user_prompt: Prompt, semantic_models: List[TableDescription], model) -> str:
        prompt = ChatPromptTemplate.from_template(SEMANTIC_MODEL_SQL_GENERATOR)
        parser = JsonOutputParser(pydantic_object=SQLGenerationOutput)

        chain = prompt | model | parser

        ddl_commands = [{ "table_name":f'{semantic_model.schema_name}.{semantic_model.table_name}', "ddl":semantic_model.table_schema}
                         for semantic_model in semantic_models]
        output = chain.invoke({"USER_QUESTION": user_prompt.text, "CONTEXT": ddl_commands})
        return output["sql_query"]



    @override
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
        metadata: dict = None,
    ) -> SQLGeneration:
        prompt = ChatPromptTemplate.from_template(SEMANTIC_MODEL_CLASSIFICATION)
        model = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=self.llm_config.llm_name,
            api_base=self.llm_config.api_base)
        parser = JsonOutputParser(pydantic_object=QuestionClassificationOutput)
        chain = prompt | model | parser
        storage = self.system.instance(DB)
        repository = TableDescriptionRepository(storage)
        semantic_models = repository.get_all_tables_by_db(
            {
                "db_connection_id": str(database_connection.id),
                "status": TableDescriptionStatus.SCANNED.value,
                "table_name": "employee"
            }
        )
        response = chain.invoke(
            {"USER_QUESTION": user_prompt.text, "SEMANTIC_MODELS": semantic_models[0:8]})

        if response["need_feedback"] == "Yes":
            return SQLGeneration(
                prompt_id=user_prompt.id,
                completed_at= datetime.now(),
                sql = '',
                status="NEEDS_FEEDBACK",
                error=response["reasoning"]
            )

        else:  # noqa: RET505
            sql = self.generate_sql_query(user_prompt, semantic_models, model)
            try:
                sql_query = self.execute_sql_query_and_recover(database_connection, sql)
                return SQLGeneration(
                    prompt_id=user_prompt.id,
                    completed_at= datetime.now(),
                    sql = sql,
                    status="SUCCESS",
                    error=None
                )
            except TimeoutError as e:
                return "SQL query execution time exceeded, proceed without query execution"


        return None

    @override
    def stream_response(
            self,
            user_prompt: Prompt,
            database_connection: DatabaseConnection,
            response: SQLGeneration,
            queue: Queue,
            metadata: dict = None,
        ):
            pass

