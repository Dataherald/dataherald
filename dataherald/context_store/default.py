import logging
from typing import Any, List

from bson.objectid import ObjectId
from overrides import override
from sql_metadata import Parser

from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)

class DefaultContextStore(ContextStore):
    

    def __init__(self, system: System):
        super().__init__(system)

    @override
    def retrieve_context_for_question(self, nl_question: str) -> str | None:
        logger.info(f'getting context for {nl_question}')

        closest_questions = self.vector_store.query(
            query_texts = [nl_question],
            collection = self.golden_record_collection,
            num_results = 3
        )

        samples = []
        print(closest_questions)
        for id in closest_questions['ids']:
            golden_query = self.db.find_one("nl_query_response", {"nl_question_id": ObjectId(id[0])})
            if golden_query is not None:
                samples.append(golden_query)
        print(samples)
        if len(samples) == 0:
            return None
        else:
            return f"Question: {closest_questions['documents'][0][0]} \n SQL: {samples[0]['sql_query']} \n"

    @override
    def add_golden_records(self, golden_records: List) -> bool:
        """Creates embeddings of the questions and adds them to the VectorDB. Also adds the golden records to the DB"""
        for record in golden_records:
            tables = Parser(record['sql']).tables
            question = record['nl_question']
            user_question = NLQuery(question=question)
            user_question.id = self.db.insert_one("nl_question", user_question.dict())
            self.vector_store.add_record(
                documents = question,
                collection = self.golden_record_collection,
                metadata = [{'tables_used':tables[0]}], #this should be updated for multiple tables
                ids=[str(user_question.id)]
            )
            nlqueryresponse_object = NLQueryResponse(
                nl_question_id=user_question.id,
                sql_query=record['sql'],
                golden_record=True
            )
            self.db.insert_one("nl_query_response", nlqueryresponse_object.dict())
        return True

    @override
    def add_table_metadata(self, table_name: str, table_metadata: dict) -> bool:
        return super().add_table_metadata(table_name, table_metadata)


