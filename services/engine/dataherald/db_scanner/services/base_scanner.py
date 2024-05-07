import sqlalchemy
from overrides import override
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column

from dataherald.db_scanner.models.types import QueryHistory
from dataherald.db_scanner.services.abstract_scanner import AbstractScanner
from dataherald.sql_database.base import SQLDatabase

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 100


class BaseScanner(AbstractScanner):
    @override
    def cardinality_values(self, column: Column, db_engine: SQLDatabase) -> list | None:
        cardinality_query = sqlalchemy.select([func.distinct(column)]).limit(101)
        cardinality = db_engine.engine.execute(cardinality_query).fetchall()

        if MAX_CATEGORY_VALUE > len(cardinality) > MIN_CATEGORY_VALUE:
            return [str(category[0]) for category in cardinality]
        return None

    @override
    def get_logs(
        self, table: str, db_engine: SQLDatabase, db_connection_id: str  # noqa: ARG002
    ) -> list[QueryHistory]:
        return []
