import logging
from datetime import datetime
from typing import Any, List

import sqlalchemy
from clickhouse_sqlalchemy import engines
from overrides import override
from sqlalchemy import Column, MetaData, Table, inspect
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql.sqltypes import NullType

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
from dataherald.db_scanner.services.click_house_scanner import ClickHouseScanner
from dataherald.db_scanner.services.postgre_sql_scanner import PostgreSqlScanner
from dataherald.db_scanner.services.redshift_scanner import RedshiftScanner
from dataherald.db_scanner.services.snowflake_scanner import SnowflakeScanner
from dataherald.db_scanner.services.sql_server_scanner import SqlServerScanner
from dataherald.sql_database.base import SQLDatabase
from dataherald.types import ScannerRequest

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 60
MAX_SIZE_LETTERS = 50

logger = logging.getLogger(__name__)


class SqlAlchemyScanner(Scanner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def create_tables(
        self,
        tables: list[str],
        db_connection_id: str,
        schema: str,
        repository: TableDescriptionRepository,
        metadata: dict = None,
    ) -> None:
        for table in tables:
            repository.save_table_info(
                TableDescription(
                    db_connection_id=db_connection_id,
                    schema_name=schema,
                    table_name=table,
                    status=TableDescriptionStatus.NOT_SCANNED.value,
                    metadata=metadata,
                )
            )

    @override
    def refresh_tables(
        self,
        schemas_and_tables: dict[str, list],
        db_connection_id: str,
        repository: TableDescriptionRepository,
        metadata: dict = None,
    ) -> list[TableDescription]:
        rows = []
        for schema, tables in schemas_and_tables.items():
            stored_tables = repository.find_by(
                {"db_connection_id": str(db_connection_id), "schema_name": schema}
            )
            stored_tables_list = [table.table_name for table in stored_tables]

            for table_description in stored_tables:
                if table_description.table_name not in tables:
                    table_description.status = TableDescriptionStatus.DEPRECATED.value
                    rows.append(repository.save_table_info(table_description))
                else:
                    rows.append(TableDescription(**table_description.dict()))

            for table in tables:
                if table not in stored_tables_list:
                    rows.append(
                        repository.save_table_info(
                            TableDescription(
                                db_connection_id=db_connection_id,
                                table_name=table,
                                status=TableDescriptionStatus.NOT_SCANNED.value,
                                metadata=metadata,
                                schema_name=schema,
                            )
                        )
                    )
        return rows

    @override
    def synchronizing(
        self,
        scanner_request: ScannerRequest,
        repository: TableDescriptionRepository,
    ) -> list[TableDescription]:
        rows = []
        for id in scanner_request.ids:
            table_description = repository.find_by_id(id)
            rows.append(
                repository.save_table_info(
                    TableDescription(
                        db_connection_id=table_description.db_connection_id,
                        table_name=table_description.table_name,
                        status=TableDescriptionStatus.SYNCHRONIZING.value,
                        metadata=scanner_request.metadata,
                        schema_name=table_description.schema_name,
                    )
                )
            )
        return rows

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
        self,
        meta: MetaData,
        table: str,
        column: dict,
        db_engine: SQLDatabase,
        scanner_service: AbstractScanner,
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
        category_values = scanner_service.cardinality_values(
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
        print(f"Create table schema for: {table}")

        original_table = next((x for x in meta.sorted_tables if x.name == table), None)
        if original_table is None:
            raise ValueError(f"Table '{table}' not found in metadata.")

        valid_columns = []
        for col in original_table.columns:
            if isinstance(col.type, NullType):
                logger.warning(
                    f"Column {col} is ignored due to its NullType data type which is not supported"
                )
                continue
            valid_columns.append(col)

        new_columns = [
            Column(
                col.name,
                col.type,
                primary_key=col.primary_key,
                autoincrement=col.autoincrement,
            )
            for col in valid_columns
        ]

        if "clickhouse" not in str(db_engine.engine.url).split(":")[0]:
            new_table = Table(original_table.name, MetaData(), *new_columns)
        else:
            new_table = Table(
                original_table.name, MetaData(), *new_columns, engines.MergeTree()
            )

        foreign_key_constraints = []
        for fk in original_table.foreign_keys:
            foreign_key_constraints.append(
                f"FOREIGN KEY (`{fk.parent.name}`) REFERENCES `{fk.column.table.name}` (`{fk.column.name}`)"
            )

        create_table_ddl = str(CreateTable(new_table).compile(db_engine.engine))
        create_table_ddl = (
            create_table_ddl.rstrip()[:-1].rstrip()
            + ",\n\t"
            + ",\n\t".join(foreign_key_constraints)
            + ");"
        )

        return create_table_ddl.rstrip()

    def scan_single_table(
        self,
        meta: MetaData,
        table: str,
        db_engine: SQLDatabase,
        db_connection_id: str,
        repository: TableDescriptionRepository,
        scanner_service: AbstractScanner,
        schema: str | None = None,
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
                    meta=meta,
                    table=table,
                    column=column,
                    db_engine=db_engine,
                    scanner_service=scanner_service,
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
            error_message="",
            status=TableDescriptionStatus.SCANNED.value,
            schema_name=schema,
        )

        repository.save_table_info(object)
        return object

    @override
    def scan(
        self,
        db_engine: SQLDatabase,
        table_descriptions: list[TableDescription],
        repository: TableDescriptionRepository,
        query_history_repository: QueryHistoryRepository,
    ) -> None:
        services = {
            "snowflake": SnowflakeScanner,
            "bigquery": BigQueryScanner,
            "postgresql": PostgreSqlScanner,
            "mssql": SqlServerScanner,
            "clickhouse": ClickHouseScanner,
            "redshift": RedshiftScanner,
        }
        scanner_service = BaseScanner()
        if db_engine.engine.dialect.name in services.keys():
            scanner_service = services[db_engine.engine.dialect.name]()

        inspect(db_engine.engine)
        meta = MetaData(bind=db_engine.engine)
        MetaData.reflect(meta, views=True)

        for table in table_descriptions:
            try:
                self.scan_single_table(
                    meta=meta,
                    table=table.table_name,
                    db_engine=db_engine,
                    db_connection_id=table.db_connection_id,
                    repository=repository,
                    scanner_service=scanner_service,
                    schema=table.schema_name,
                )
            except Exception as e:
                repository.save_table_info(
                    TableDescription(
                        db_connection_id=table.db_connection_id,
                        table_name=table,
                        status=TableDescriptionStatus.FAILED.value,
                        error_message=f"{e}",
                        schema_name=table.schema_name,
                    )
                )
            try:
                logger.info(f"Get logs table: {table}")
                query_history = scanner_service.get_logs(
                    table.table_name, db_engine, table.db_connection_id
                )
                if len(query_history) > 0:
                    for query in query_history:
                        query_history_repository.insert(query)

            except Exception:  # noqa: S112
                continue
