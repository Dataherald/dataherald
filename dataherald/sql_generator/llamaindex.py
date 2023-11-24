"""A wrapper for the SQL generation functions in langchain"""

import logging
import os
import time
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
from dataherald.types import Question, Response

logger = logging.getLogger(__name__)


class LlamaIndexSQLGenerator(SQLGenerator):
    llm: Any | None = None

    @override
    def generate_response(
        self,
        user_question: Question,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
        generate_csv: bool = False,
    ) -> Response:
        start_time = time.time()
        logger.info(f"Generating SQL response to question: {str(user_question.dict())}")
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
                    f"Question: {sample['nl_question']} \nSQL: {sample['sql_query']} \n"
                )
        question_with_context = (
            f"{user_question.question} An example of a similar question and the query that was generated to answer it \
                                 is the following {samples_prompt_string}"
            if context is not None
            else user_question.question
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
        exec_time = time.time() - start_time
        response = Response(
            question_id=user_question.id,
            response=result.response,
            exec_time=exec_time,
            total_tokens=token_counter.total_llm_token_count,
            total_cost=total_cost,
            intermediate_steps=[str(result.metadata)],
            sql_query=self.format_sql_query(result.metadata["sql_query"]),
        )
        return self.create_sql_query_status(
            self.database,
            response.sql_query,
            response,
            generate_csv=generate_csv,
            database_connection=database_connection,
        )
