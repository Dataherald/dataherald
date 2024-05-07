from overrides import override
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.schema import Column

from dataherald.db_scanner.models.types import QueryHistory
from dataherald.db_scanner.services.abstract_scanner import AbstractScanner
from dataherald.sql_database.base import SQLDatabase

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 100
MAX_LOGS = 5_000


class SqlServerScanner(AbstractScanner):
    @override
    def cardinality_values(self, column: Column, db_engine: SQLDatabase) -> list | None:
        try:
            count_query = f"SELECT APPROX_COUNT_DISTINCT({column.name}) FROM {column.table.name}"  # noqa: S608
            rs = db_engine.engine.execute(count_query).fetchall()
        except SQLAlchemyError:
            return None

        if (
            len(rs) > 0
            and len(rs[0]) > 0
            and MIN_CATEGORY_VALUE < rs[0][0] <= MAX_CATEGORY_VALUE
        ):
            cardinality_query = f"SELECT TOP 101 {column.name} FROM (SELECT DISTINCT {column.name} FROM [{column.table.name}]) AS subquery;"  # noqa: E501 S608
            cardinality = db_engine.engine.execute(cardinality_query).fetchall()
            return [str(category[0]) for category in cardinality]

        return None

    @override
    def get_logs(
        self, table: str, db_engine: SQLDatabase, db_connection_id: str  # noqa: ARG002
    ) -> list[QueryHistory]:
        return []
