"""A wrapper for the SQL generation functions in langchain"""
import datetime
import logging
import os
from typing import Any, List

import tiktoken
from langchain.callbacks.openai_info import MODEL_COST_PER_1K_TOKENS
from llama_index import (
    LLMPredictor,
    ServiceContext,
    VectorStoreIndex,
)
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from overrides import override
from sqlalchemy import MetaData

from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.types import Prompt, SQLGeneration

logger = logging.getLogger(__name__)


class LlamaIndexSQLGenerator(SQLGenerator):
    llm: Any | None = None

    @override
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
    ) -> SQLGeneration:
        logger.info(f"Generating SQL response to question: {str(user_prompt.dict())}")
        response = SQLGeneration(
            prompt_id=user_prompt.id,
            created_at=datetime.datetime.now(),
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=os.getenv("LLM_MODEL", "gpt-4-1106-preview"),
        )
        token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(self.llm.model_name).encode,
            verbose=False,  # set to true to see usage printed to the console
        )
        callback_manager = CallbackManager([token_counter])
        self.database = SQLDatabase.get_sql_engine(database_connection)
        db_engine = self.database.engine
        # load all table definitions
        metadata_obj = MetaData()
        metadata_obj.reflect(db_engine)
        table_schema_objs = []
        table_node_mapping = SQLTableNodeMapping(self.database)
        if context is not None:
            samples_prompt_string = "The following are some similar previous questions and their correct SQL queries from these databases: \
            \n"
            for sample in context:
                samples_prompt_string += (
                    f"Question: {sample['prompt_text']} \nSQL: {sample['sql']} \n"
                )
        question_with_context = (
            f"{user_prompt.text} An example of a similar question and the query that was generated to answer it \
                                 is the following {samples_prompt_string}"
            if context is not None
            else user_prompt.text
        )
        for table_name in metadata_obj.tables.keys():
            table_schema_objs.append(SQLTableSchema(table_name=table_name))

        llm_predictor = LLMPredictor(llm=self.llm)
        service_context = ServiceContext.from_defaults(
            llm_predictor=llm_predictor, callback_manager=callback_manager
        )

        obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex,
        )
        print(question_with_context)

        # We construct a SQLTableRetrieverQueryEngine.
        # Note that we pass in the ObjectRetriever so that we can dynamically retrieve the table during query-time.
        # ObjectRetriever: A retriever that retrieves a set of query engine tools.
        query_engine = SQLTableRetrieverQueryEngine(
            self.database,
            obj_index.as_retriever(similarity_top_k=1),
            service_context=service_context,
        )
        result = query_engine.query(question_with_context)
        total_cost = (
            token_counter.total_llm_token_count
            * MODEL_COST_PER_1K_TOKENS[self.llm.model_name]
        )
        logger.info(
            f"total cost: {str(total_cost)} {str(token_counter.total_llm_token_count)}"
        )
        response.tokens_used = token_counter.total_llm_token_count
        response.sql = self.format_sql_query(result.metadata["sql_query"])
        response.completed_at = datetime.datetime.now()
        return self.create_sql_query_status(
            self.database,
            response.sql,
            response,
        )
