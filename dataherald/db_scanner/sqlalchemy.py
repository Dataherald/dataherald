from sqlalchemy import MetaData, create_engine, text, inspect, select
from dataherald.sql_database.base import SQLDatabase
from dataherald.db_scanner import Scanner
from overrides import override
from dataherald.db_scanner.models.types import TableSchemaDetail, ColumnDetail
import sqlalchemy
from sqlalchemy.schema import CreateTable
from dataherald.db_scanner.repository.base import DBScannerRepository



class SqlAlchemyScanner(Scanner):
    def scan_single_table(self, table: str, db_engine: SQLDatabase, db_alias: str, repository: DBScannerRepository) -> TableSchemaDetail:
        # todo refactor this line
        inspector = inspect(db_engine.engine)
        meta = MetaData(bind=db_engine.engine)

        MetaData.reflect(meta)

        print(f"Scanning table: {table}")
        table_columns = []
        columns = inspector.get_columns(table_name=table)

        # Create examples
        examples = db_engine.engine.execute(f'Select * from {table} limit 3')
        examples_dict = []
        for example in examples:
            print(f"Create examples: {table}")
            temp_dict = {}
            for index, value in enumerate(examples.keys()):
                temp_dict[value] = str(example[index])
            examples_dict.append(temp_dict)

        for column in columns:
            print(f"Scanning column: {column}")
            DYNAMIC_META_TABLE = meta.tables[table]
            query = sqlalchemy.select([
                DYNAMIC_META_TABLE.c[column['name']],
                sqlalchemy.func.count(DYNAMIC_META_TABLE.c[column['name']])
            ]).group_by(DYNAMIC_META_TABLE.c[column['name']])

            # get all the records
            categories = db_engine.engine.execute(query).fetchall()

            table_column = ColumnDetail(
                name=column['name'],
                data_type=str(column['type']),
                low_cardinality=False,
            )

            if 1 < len(categories) <= 60:
                table_column = ColumnDetail(
                    name=column['name'],
                    data_type=str(column['type']),
                    low_cardinality=True,
                    categories=[str(category[0]) for category in categories]
                )

            table_columns.append(table_column)

        # Create table schema
        print(f"Create table schema: {table}")
        create_table = str(
            CreateTable([x for x in meta.sorted_tables if x.name == table][0]).compile(db_engine.engine))
        table_info = f"{create_table.rstrip()}"

        object = TableSchemaDetail(
            db_alias=db_alias,
            table_name=table,
            columns=table_columns,
            table_schema=table_info,
            examples=examples_dict
        )

        repository.save_table_info(object)
        return object

    @override
    def scan(self, db_engine: SQLDatabase, db_alias: str, repository: DBScannerRepository) -> None:
        inspector = inspect(db_engine.engine)
        tables = [inspector.get_table_names()[0]]

        result = []
        for table in tables:
            obj = self.scan_single_table(table, db_engine, db_alias, repository)
            result.append(obj)
        return None
