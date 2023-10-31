import logging
from typing import List, Tuple

from overrides import override
from sql_metadata import Parser

from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.repositories.golden_records import GoldenRecordRepository
from dataherald.repositories.instructions import InstructionRepository
from dataherald.types import GoldenRecord, GoldenRecordRequest, Question

logger = logging.getLogger(__name__)


class DefaultContextStore(ContextStore):
    def __init__(self, system: System):
        super().__init__(system)

    @override
    def retrieve_context_for_question(
        self, nl_question: Question, number_of_samples: int = 3
    ) -> Tuple[List[dict] | None, List[dict] | None]:
        logger.info(f"Getting context for {nl_question.question}")
        closest_questions = self.vector_store.query(
            query_texts=[nl_question.question],
            db_connection_id=nl_question.db_connection_id,
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
            samples = None
        instructions = []
        instruction_repository = InstructionRepository(self.db)
        all_instructions = instruction_repository.find_all()
        for instruction in all_instructions:
            if instruction.db_connection_id == nl_question.db_connection_id:
                instructions.append(
                    {
                        "instruction": instruction.instruction,
                    }
                )
        if len(instructions) == 0:
            instructions = None

        return samples, instructions

    @override
    def add_golden_records(
        self, golden_records: List[GoldenRecordRequest]
    ) -> List[GoldenRecord]:
        """Creates embeddings of the questions and adds them to the VectorDB. Also adds the golden records to the DB"""
        golden_records_repository = GoldenRecordRepository(self.db)
        retruned_golden_records = []
        for record in golden_records:
            tables = Parser(record.sql_query).tables
            question = record.question
            golden_record = GoldenRecord(
                question=question,
                sql_query=record.sql_query,
                db_connection_id=record.db_connection_id,
            )
            retruned_golden_records.append(golden_record)
            golden_record = golden_records_repository.insert(golden_record)
            self.vector_store.add_record(
                documents=question,
                db_connection_id=record.db_connection_id,
                collection=self.golden_record_collection,
                metadata=[
                    {
                        "tables_used": tables[0],
                        "db_connection_id": record.db_connection_id,
                    }
                ],  # this should be updated for multiple tables
                ids=[str(golden_record.id)],
            )
        return retruned_golden_records

    @override
    def remove_golden_records(self, ids: List) -> bool:
        """Removes the golden records from the DB and the VectorDB"""
        golden_records_repository = GoldenRecordRepository(self.db)
        for id in ids:
            self.vector_store.delete_record(
                collection=self.golden_record_collection, id=id
            )
            deleted = golden_records_repository.delete_by_id(id)
            if deleted == 0:
                logger.warning(f"Golden record with id {id} not found")
        return True
