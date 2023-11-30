import sqlalchemy
from overrides import override
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column

from dataherald.db_scanner.models.types import QueryHistory
from dataherald.db_scanner.services.abstract_scanner import AbstractScanner
from dataherald.sql_database.base import SQLDatabase

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 100


class BigQueryScanner(AbstractScanner):
    @override
    def cardinality_values(self, column: Column, db_engine: SQLDatabase) -> list | None:
        rs = db_engine.engine.execute(
            f"SELECT APPROX_COUNT_DISTINCT({column.name}) FROM {column.table.name}"  # noqa: S608 E501
        ).fetchall()

        if (
            len(rs) > 0
            and len(rs[0]) > 0
            and MIN_CATEGORY_VALUE < rs[0][0] <= MAX_CATEGORY_VALUE
        ):
            cardinality_query = sqlalchemy.select([func.distinct(column)]).limit(101)
            cardinality = db_engine.engine.execute(cardinality_query).fetchall()
            return [str(category[0]) for category in cardinality]

        return None

    @override
    def get_logs(
        self, table: str, db_engine: SQLDatabase, db_connection_id: str
    ) -> list[QueryHistory]:
        # todo fix hardcoded date
        rows = db_engine.engine.execute(
            f"SELECT query, count(*) as total FROM `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`, UNNEST(referenced_tables) AS t where job_type = 'QUERY' and statement_type = 'SELECT' and t.table_id = '{table}' and state = 'DONE' and creation_time >='2023-11-01' group by query ORDER BY total DESC limit 20"  # noqa: S608 E501
        ).fetchall()
        return [
            QueryHistory(
                db_connection_id=db_connection_id,
                table_name=table,
                query=row[0],
                coincidences=row[1],
            )
            for row in rows
        ]
