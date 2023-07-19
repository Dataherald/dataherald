import logging
from typing import List

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
    def retrieve_context_for_question(self, nl_question: NLQuery) -> str | None:
        logger.info(f"getting context for {nl_question.question}")

        closest_questions = self.vector_store.query(
            query_texts=[nl_question.question],
            db_alias=nl_question.db_alias,
            collection=self.golden_record_collection,
            num_results=3,
        )

        samples = []
        for question in closest_questions:
            golden_query = self.db.find_one(
                "nl_query_response", {"nl_question_id": ObjectId(question["id"])}
            )
            associated_nl_question = self.db.find_by_id("nl_question", question["id"])
            if golden_query is not None and associated_nl_question is not None:
                samples.append(
                    {
                        "nl_question": associated_nl_question["question"],
                        "sql_query": golden_query["sql_query"],
                    }
                )
        if len(samples) == 0:
            return None

        samples_prompt_string = "The following are some similar previous questions and their correct SQL queries from these databases: \n"
        for sample in samples:
            samples_prompt_string += (
                f"Question: {sample['nl_question']} \nSQL: {sample['sql_query']} \n"
            )

        return samples_prompt_string

    @override
    def add_golden_records(self, golden_records: List) -> bool:
        """Creates embeddings of the questions and adds them to the VectorDB. Also adds the golden records to the DB"""
        for record in golden_records:
            tables = Parser(record["sql"]).tables
            question = record["nl_question"]
            user_question = NLQuery(question=question, db_alias=record["db"])
            user_question.id = self.db.insert_one("nl_question", user_question.dict())
            self.vector_store.add_record(
                documents=question,
                collection=self.golden_record_collection,
                metadata=[
                    {"tables_used": tables[0], "db_alias": record["db"]}
                ],  # this should be updated for multiple tables
                ids=[str(user_question.id)],
            )
            nlqueryresponse_object = NLQueryResponse(
                nl_question_id=user_question.id,
                sql_query=record["sql"],
                golden_record=True,
            )
            self.db.insert_one("nl_query_response", nlqueryresponse_object.dict())
        return True

    @override
    def add_table_metadata(self, table_name: str, table_metadata: dict) -> bool:
        return super().add_table_metadata(table_name, table_metadata)
