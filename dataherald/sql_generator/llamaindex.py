"""A wrapper for the SQL generation functions in langchain"""

import logging

from llama_index import (
    LLMPredictor,
    ServiceContext,
    VectorStoreIndex,
)
from llama_index.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from overrides import override
from sqlalchemy import MetaData

from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


class LlamaIndexSQLGenerator(SQLGenerator):
    @override
    def generate_response(
        self,
        user_question: NLQuery,
        database_connection: DatabaseConnection,
        context: str = None,
    ) -> NLQueryResponse:
        logger.info(f"Generating SQL response to question: {str(user_question.dict())}")
        self.database = SQLDatabase.get_sql_engine(database_connection)
        db_engine = self.database.engine
        # load all table definitions
        metadata_obj = MetaData()
        metadata_obj.reflect(db_engine)
        table_schema_objs = []
        table_node_mapping = SQLTableNodeMapping(self.database)
        question_with_context = (
            f"{user_question.question} An example of a similar question and the query that was generated to answer it \
                                 is the following {context}"
            if context is not None
            else user_question.question
        )
        for table_name in metadata_obj.tables.keys():
            table_schema_objs.append(SQLTableSchema(table_name=table_name))

        llm_predictor = LLMPredictor(llm=self.llm)
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

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
        return NLQueryResponse(
            nl_question_id=user_question.id,
            nl_response=result.response,
            intermediate_steps=[str(result.metadata)],
            sql_query=result.metadata["sql_query"],
        )
