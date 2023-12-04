import logging
from datetime import datetime
from typing import Any, List

import sqlalchemy
from overrides import override
from sqlalchemy import MetaData, inspect
from sqlalchemy.schema import CreateTable

from dataherald.db_scanner import Scanner
from dataherald.db_scanner.models.types import (
    ColumnDetail,
    TableDescription,
    TableDescriptionStatus,
)
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.db_scanner.repository.query_history import QueryHistoryRepository
from dataherald.db_scanner.services.abstract_scanner import AbstractScanner
from dataherald.db_scanner.services.base_scanner import BaseScanner
from dataherald.db_scanner.services.big_query_scanner import BigQueryScanner
from dataherald.db_scanner.services.postgre_sql_scanner import PostgreSqlScanner
from dataherald.db_scanner.services.snowflake_scanner import SnowflakeScanner
from dataherald.sql_database.base import SQLDatabase

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 60
MAX_SIZE_LETTERS = 50

logger = logging.getLogger(__name__)


class SqlAlchemyScanner(Scanner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scanner_service: AbstractScanner = None

    @override
    def synchronizing(
        self,
        tables: list[str],
        db_connection_id: str,
        repository: TableDescriptionRepository,
    ) -> None:
        # persist tables to be scanned
        for table in tables:
            repository.save_table_info(
                TableDescription(
                    db_connection_id=db_connection_id,
                    table_name=table,
                    status=TableDescriptionStatus.SYNCHRONIZING.value,
                )
            )

    @override
    def get_all_tables_and_views(self, database: SQLDatabase) -> list[str]:
        inspector = inspect(database.engine)
        meta = MetaData(bind=database.engine)
        MetaData.reflect(meta, views=True)
        return inspector.get_table_names() + inspector.get_view_names()

    def get_table_examples(
        self, meta: MetaData, db_engine: SQLDatabase, table: str, rows_number: int = 3
    ) -> List[Any]:
        print(f"Create examples: {table}")
        examples_query = (
            sqlalchemy.select(meta.tables[table])
            .with_only_columns(
                [
                    column
                    for column in meta.tables[table].columns
                    if column.name.find(".") < 0
                ]
            )
            .limit(rows_number)
        )
        examples = db_engine.engine.execute(examples_query).fetchall()
        examples_dict = []
        columns = [column["name"] for column in examples_query.column_descriptions]
        for example in examples:
            temp_dict = {}
            for index, value in enumerate(columns):
                temp_dict[value] = str(example[index])
            examples_dict.append(temp_dict)
        return examples_dict

    def get_processed_column(  # noqa: PLR0911
        self, meta: MetaData, table: str, column: dict, db_engine: SQLDatabase
    ) -> ColumnDetail:
        dynamic_meta_table = meta.tables[table]

        field_size_query = sqlalchemy.select(
            [dynamic_meta_table.c[column["name"]]]
        ).limit(1)

        field_size = db_engine.engine.execute(field_size_query).first()
        # Check if the column is empty
        if not field_size:
            field_size = [""]
        if len(str(str(field_size[0]))) > MAX_SIZE_LETTERS:
            return ColumnDetail(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=False,
            )
        category_values = self.scanner_service.cardinality_values(
            dynamic_meta_table.c[column["name"]], db_engine
        )
        if category_values:
            return ColumnDetail(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=True,
                categories=category_values,
            )
        return ColumnDetail(
            name=column["name"],
            data_type=str(column["type"]),
            low_cardinality=False,
        )

    def get_table_schema(
        self, meta: MetaData, db_engine: SQLDatabase, table: str
    ) -> str:
        print(f"Create table schema: {table}")
        create_table = str(
            CreateTable([x for x in meta.sorted_tables if x.name == table][0]).compile(
                db_engine.engine
            )
        )
        return f"{create_table.rstrip()}"

    def scan_single_table(
        self,
        meta: MetaData,
        table: str,
        db_engine: SQLDatabase,
        db_connection_id: str,
        repository: TableDescriptionRepository,
    ) -> TableDescription:
        print(f"Scanning table: {table}")
        inspector = inspect(db_engine.engine)
        table_columns = []
        columns = inspector.get_columns(table_name=table)
        columns = [column for column in columns if column["name"].find(".") < 0]

        for column in columns:
            print(f"Scanning column: {column['name']}")
            table_columns.append(
                self.get_processed_column(
                    meta=meta, table=table, column=column, db_engine=db_engine
                )
            )

        object = TableDescription(
            db_connection_id=db_connection_id,
            table_name=table,
            columns=table_columns,
            table_schema=self.get_table_schema(
                meta=meta, db_engine=db_engine, table=table
            ),
            examples=self.get_table_examples(
                meta=meta, db_engine=db_engine, table=table, rows_number=3
            ),
            last_schema_sync=datetime.now(),
            status=TableDescriptionStatus.SYNCHRONIZED.value,
        )

        repository.save_table_info(object)
        return object

    @override
    def scan(
        self,
        db_engine: SQLDatabase,
        db_connection_id: str,
        table_names: list[str] | None,
        repository: TableDescriptionRepository,
        query_history_repository: QueryHistoryRepository,
    ) -> None:
        services = {
            "snowflake": SnowflakeScanner,
            "bigquery": BigQueryScanner,
            "psycopg2": PostgreSqlScanner,
        }
        self.scanner_service = BaseScanner()
        if db_engine.engine.driver in services.keys():
            self.scanner_service = services[db_engine.engine.driver]()

        inspector = inspect(db_engine.engine)
        meta = MetaData(bind=db_engine.engine)
        MetaData.reflect(meta, views=True)
        tables = inspector.get_table_names() + inspector.get_view_names()
        if table_names:
            table_names = [table.lower() for table in table_names]
            tables = [
                table for table in tables if table and table.lower() in table_names
            ]
        if len(tables) == 0:
            raise ValueError("No table found")

        for table in tables:
            try:
                self.scan_single_table(
                    meta=meta,
                    table=table,
                    db_engine=db_engine,
                    db_connection_id=db_connection_id,
                    repository=repository,
                )
            except Exception as e:
                repository.save_table_info(
                    TableDescription(
                        db_connection_id=db_connection_id,
                        table_name=table,
                        status=TableDescriptionStatus.FAILED.value,
                        error_message=f"{e}",
                    )
                )
            try:
                logger.info(f"Get logs table: {table}")
                query_history = self.scanner_service.get_logs(
                    table, db_engine, db_connection_id
                )
                if len(query_history) > 0:
                    for query in query_history:
                        query_history_repository.insert(query)

            except Exception:  # noqa: S112
                continue
