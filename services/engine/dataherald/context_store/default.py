import logging
from typing import List, Tuple

from overrides import override
from sql_metadata import Parser

from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.repositories.database_connections import (
    DatabaseConnectionNotFoundError,
    DatabaseConnectionRepository,
)
from dataherald.repositories.golden_sqls import GoldenSQLRepository
from dataherald.repositories.instructions import InstructionRepository
from dataherald.types import GoldenSQL, GoldenSQLRequest, Prompt
from dataherald.utils.sql_utils import extract_the_schemas_from_sql

logger = logging.getLogger(__name__)


class MalformedGoldenSQLError(Exception):
    pass


class DefaultContextStore(ContextStore):
    def __init__(self, system: System):
        super().__init__(system)

    @override
    def retrieve_context_for_question(
        self, prompt: Prompt, number_of_samples: int = 3
    ) -> Tuple[List[dict] | None, List[dict] | None]:
        logger.info(f"Getting context for {prompt.text}")
        closest_questions = self.vector_store.query(
            query_texts=[prompt.text],
            db_connection_id=prompt.db_connection_id,
            collection=self.golden_sql_collection,
            num_results=number_of_samples,
        )

        samples = []
        golden_sqls_repository = GoldenSQLRepository(self.db)
        for question in closest_questions:
            golden_sql = golden_sqls_repository.find_by_id(question["id"])
            if golden_sql is not None:
                samples.append(
                    {
                        "prompt_text": golden_sql.prompt_text,
                        "sql": golden_sql.sql,
                        "score": question["score"],
                    }
                )
        if len(samples) == 0:
            samples = None
        instructions = []
        instruction_repository = InstructionRepository(self.db)
        all_instructions = instruction_repository.find_all()
        for instruction in all_instructions:
            if instruction.db_connection_id == prompt.db_connection_id:
                instructions.append(
                    {
                        "instruction": instruction.instruction,
                    }
                )
        if len(instructions) == 0:
            instructions = None

        return samples, instructions

    @override
    def add_golden_sqls(self, golden_sqls: List[GoldenSQLRequest]) -> List[GoldenSQL]:
        """Creates embeddings of the questions and adds them to the VectorDB. Also adds the golden sqls to the DB"""
        golden_sqls_repository = GoldenSQLRepository(self.db)
        db_connection_repository = DatabaseConnectionRepository(self.db)
        stored_golden_sqls = []
        for record in golden_sqls:
            try:
                Parser(record.sql).tables  # noqa: B018
            except Exception as e:
                raise MalformedGoldenSQLError(
                    f"SQL {record.sql} is malformed. Please check the syntax."
                ) from e

            db_connection = db_connection_repository.find_by_id(record.db_connection_id)
            if not db_connection:
                raise DatabaseConnectionNotFoundError(
                    f"Database connection not found, {record.db_connection_id}"
                )

            if db_connection.schemas:
                schema_not_found = True
                used_schemas = extract_the_schemas_from_sql(record.sql)
                for schema in db_connection.schemas:
                    if schema in used_schemas:
                        schema_not_found = False
                        break
                if schema_not_found:
                    raise MalformedGoldenSQLError(
                        f"SQL {record.sql} does not contain any of the schemas {db_connection.schemas}"
                    )

            prompt_text = record.prompt_text
            golden_sql = GoldenSQL(
                prompt_text=prompt_text,
                sql=record.sql,
                db_connection_id=record.db_connection_id,
                metadata=record.metadata,
            )
            stored_golden_sqls.append(golden_sqls_repository.insert(golden_sql))
        self.vector_store.add_records(stored_golden_sqls, self.golden_sql_collection)
        return stored_golden_sqls

    @override
    def remove_golden_sqls(self, ids: List) -> bool:
        """Removes the golden sqls from the DB and the VectorDB"""
        golden_sqls_repository = GoldenSQLRepository(self.db)
        for id in ids:
            self.vector_store.delete_record(
                collection=self.golden_sql_collection, id=id
            )
            deleted = golden_sqls_repository.delete_by_id(id)
            if deleted == 0:
                logger.warning(f"Golden record with id {id} not found")
        return True
