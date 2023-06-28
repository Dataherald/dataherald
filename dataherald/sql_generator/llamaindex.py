"""A wrapper for the SQL generation functions in langchain"""

import logging

from llama_index import LLMPredictor, ServiceContext, SQLDatabase, VectorStoreIndex
from llama_index.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from overrides import override
from sqlalchemy import MetaData

from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


class LlamaIndexSQLGenerator(SQLGenerator):
    @override
    def generate_response(self, user_question: NLQuery) -> NLQueryResponse:
        logger.info("Generating SQL response to question: " + user_question.dict())

        db_engine = self.database.engine()
        # load all table definitions
        metadata_obj = MetaData()
        metadata_obj.reflect(db_engine)

        sql_database = SQLDatabase(db_engine)

        table_schema_objs = []
        table_node_mapping = SQLTableNodeMapping(sql_database)
        for table_name in metadata_obj.tables.keys():
            table_schema_objs.append(SQLTableSchema(table_name=table_name))

        llm_predictor = LLMPredictor(llm=self.llm)
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

        obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex,
        )

        # We construct a SQLTableRetrieverQueryEngine.
        # Note that we pass in the ObjectRetriever so that we can dynamically retrieve the table during query-time.
        # ObjectRetriever: A retriever that retrieves a set of query engine tools.
        query_engine = SQLTableRetrieverQueryEngine(
            sql_database,
            obj_index.as_retriever(similarity_top_k=1),
            service_context=service_context,
        )

        result = query_engine.query(user_question)

        return NLQueryResponse(
            nl_question_id=user_question.id,
            nl_response=result,
            intermediate_steps=[str(result.metadata)],
            sql_query=result.metadata["sql_query"],
        )
