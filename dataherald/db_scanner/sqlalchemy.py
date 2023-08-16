from typing import Any, List

import sqlalchemy
from overrides import override
from sqlalchemy import MetaData, inspect
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import func

from dataherald.db_scanner import Scanner
from dataherald.db_scanner.models.types import ColumnDetail, TableSchemaDetail
from dataherald.db_scanner.repository.base import DBScannerRepository
from dataherald.sql_database.base import SQLDatabase

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 60
MAX_SIZE_LETTERS = 50


class SqlAlchemyScanner(Scanner):
    def get_table_examples(
        self, meta: MetaData, db_engine: SQLDatabase, table: str, rows_number: int = 3
    ) -> List[Any]:
        examples_query = sqlalchemy.select(meta.tables[table]).limit(rows_number)
        examples = db_engine.engine.execute(examples_query).fetchall()
        examples_dict = []
        print(f"Create examples: {table}")
        columns = [column["name"] for column in examples_query.column_descriptions]
        for example in examples:
            temp_dict = {}
            for index, value in enumerate(columns):
                temp_dict[value] = str(example[index])
            examples_dict.append(temp_dict)
        return examples_dict

    def get_processed_column(
        self, meta: MetaData, table: str, column: dict, db_engine: SQLDatabase
    ) -> ColumnDetail:
        dynamic_meta_table = meta.tables[table]

        field_size_query = sqlalchemy.select(
            [dynamic_meta_table.c[column["name"]]]
        ).limit(1)

        field_size = db_engine.engine.execute(field_size_query).first()
        if not field_size:
            field_size = [""]
        if len(str(str(field_size[0]))) > MAX_SIZE_LETTERS:
            return ColumnDetail(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=False,
            )
        try:
            cardinality_query = sqlalchemy.select(
                [func.distinct(dynamic_meta_table.c[column["name"]])]
            ).limit(200)
            cardinality = db_engine.engine.execute(cardinality_query).fetchall()
        except Exception:
            return ColumnDetail(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=False,
            )

        if len(cardinality) > MAX_CATEGORY_VALUE:
            return ColumnDetail(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=False,
            )

        query = sqlalchemy.select(
            [
                dynamic_meta_table.c[column["name"]],
                sqlalchemy.func.count(dynamic_meta_table.c[column["name"]]),
            ]
        ).group_by(dynamic_meta_table.c[column["name"]])

        # get rows
        categories = db_engine.engine.execute(query).fetchall()
        if MIN_CATEGORY_VALUE < len(categories) <= MAX_CATEGORY_VALUE:
            return ColumnDetail(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=True,
                categories=[str(category[0]) for category in categories],
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
        db_alias: str,
        repository: DBScannerRepository,
    ) -> TableSchemaDetail:
        print(f"Scanning table: {table}")
        inspector = inspect(db_engine.engine)
        table_columns = []
        columns = inspector.get_columns(table_name=table)
        for column in columns:
            print(f"Scanning column: {column['name']}")
            table_columns.append(
                self.get_processed_column(
                    meta=meta, table=table, column=column, db_engine=db_engine
                )
            )

        object = TableSchemaDetail(
            db_alias=db_alias,
            table_name=table,
            columns=table_columns,
            table_schema=self.get_table_schema(
                meta=meta, db_engine=db_engine, table=table
            ),
            examples=self.get_table_examples(
                meta=meta, db_engine=db_engine, table=table, rows_number=3
            ),
        )

        repository.save_table_info(object)
        return object

    @override
    def scan(
        self,
        db_engine: SQLDatabase,
        db_alias: str,
        table_name: str | None,
        repository: DBScannerRepository,
    ) -> None:
        inspector = inspect(db_engine.engine)
        meta = MetaData(bind=db_engine.engine)
        MetaData.reflect(meta)
        tables = inspector.get_table_names()
        if table_name:
            tables = [table for table in tables if table.lower() == table_name.lower()]
        if len(tables) == 0:
            raise ValueError("No table found")
        result = []
        for table in tables:
            obj = self.scan_single_table(
                meta=meta,
                table=table,
                db_engine=db_engine,
                db_alias=db_alias,
                repository=repository,
            )
            result.append(obj)
