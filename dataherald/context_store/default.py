import logging
from datetime import datetime
from typing import List

from overrides import override
from sql_metadata import Parser

from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.repositories.golden_records import GoldenRecordRepository
from dataherald.types import GoldenRecord, GoldenRecordRequest, NLQuery

logger = logging.getLogger(__name__)


class DefaultContextStore(ContextStore):
    def __init__(self, system: System):
        super().__init__(system)

    @override
    def retrieve_context_for_question(
        self, nl_question: NLQuery, namespace: str, number_of_samples: int = 3
    ) -> List[dict] | None:
        logger.info(f"Getting context for {nl_question.question}")
        closest_questions = self.vector_store.query(
            query_texts=[nl_question.question],
            db_alias=nl_question.db_alias,
            namespace=namespace,
            collection=self.golden_record_collection,
            num_results=number_of_samples,
        )

        samples = []
        golden_records_repository = GoldenRecordRepository(self.db)
        for question in closest_questions:
            golden_record = golden_records_repository.find_by_id(question["id"])
            if golden_record is not None:
                samples.append(
                    {
                        "nl_question": golden_record.question,
                        "sql_query": golden_record.sql_query,
                        "score": question["score"],
                    }
                )
        if len(samples) == 0:
            return None

        return samples

    @override
    def add_golden_records(self, golden_records: List[GoldenRecordRequest], namespace: str) -> bool:
        """Creates embeddings of the questions and adds them to the VectorDB. Also adds the golden records to the DB"""
        golden_records_repository = GoldenRecordRepository(self.db)
        for record in golden_records:
            tables = Parser(record.sql).tables
            question = record.nl_question
            golden_record = GoldenRecord(
                question=question,
                sql_query=record.sql,
                db_alias=record.db,
                namespace=namespace,
                created_time=datetime.now(),
            )
            golden_record = golden_records_repository.insert(golden_record)
            self.vector_store.add_record(
                documents=question,
                namespace=namespace,
                collection=self.golden_record_collection,
                metadata=[
                    {"tables_used": tables[0], "db_alias": record.db}
                ],  # this should be updated for multiple tables
                ids=[str(golden_record.id)],
            )
        return True

    @override
    def remove_golden_records(self, ids: List, namespace: str) -> bool:
        """Removes the golden records from the DB and the VectorDB"""
        golden_records_repository = GoldenRecordRepository(self.db)
        for id in ids:
            self.vector_store.delete_record(
                namespace=namespace, collection=self.golden_record_collection, id=id
            )
            deleted = golden_records_repository.delete_by_id(id)
            if deleted == 0:
                logger.warning(f"Golden record with id {id} not found")
        return True
