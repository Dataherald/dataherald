from overrides import override
from sqlalchemy.sql.schema import Column

from dataherald.db_scanner.models.types import QueryHistory
from dataherald.db_scanner.services.abstract_scanner import AbstractScanner
from dataherald.sql_database.base import SQLDatabase

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 100


class PostgreSqlScanner(AbstractScanner):
    @override
    def cardinality_values(self, column: Column, db_engine: SQLDatabase) -> list | None:
        rs = db_engine.engine.execute(
            f"SELECT n_distinct, most_common_vals::TEXT::TEXT[] FROM pg_catalog.pg_stats WHERE tablename = '{column.table.name}' AND attname = '{column.name}'"  # noqa: S608 E501
        ).fetchall()

        if (
            len(rs) > 0
            and MIN_CATEGORY_VALUE < rs[0]["n_distinct"] <= MAX_CATEGORY_VALUE
        ):
            return rs[0]["most_common_vals"]
        return None

    @override
    def get_logs(
        self, table: str, db_engine: SQLDatabase, db_connection_id: str  # noqa: ARG002
    ) -> list[QueryHistory]:
        return []
