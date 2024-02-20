from datetime import datetime, timedelta

import sqlalchemy
from overrides import override
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column

from dataherald.db_scanner.models.types import QueryHistory
from dataherald.db_scanner.services.abstract_scanner import AbstractScanner
from dataherald.sql_database.base import SQLDatabase

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 100
MAX_LOGS = 5_000


class SnowflakeScanner(AbstractScanner):
    @override
    def cardinality_values(self, column: Column, db_engine: SQLDatabase) -> list | None:
        query = sqlalchemy.select([func.HLL(column)])
        rs = db_engine.engine.execute(query).fetchall()

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
        database_name = db_engine.engine.url.database.split("/")[0]
        filter_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        rows = db_engine.engine.execute(
            f"select QUERY_TEXT, USER_NAME, count(*) as occurrences from TABLE(INFORMATION_SCHEMA.QUERY_HISTORY()) where DATABASE_NAME = '{database_name}' and QUERY_TYPE = 'SELECT' and EXECUTION_STATUS = 'SUCCESS' and START_TIME > '{filter_date}' and QUERY_TEXT like '%FROM {table}%' and QUERY_TEXT not like '%QUERY_HISTORY%' group by QUERY_TEXT, USER_NAME ORDER BY occurrences DESC limit {MAX_LOGS}"  # noqa: S608 E501
        ).fetchall()
        return [
            QueryHistory(
                db_connection_id=db_connection_id,
                table_name=table,
                query=row[0],
                user=row[1],
                occurrences=row[2],
            )
            for row in rows
        ]
