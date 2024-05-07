from sql_metadata import Parser

from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_database.services.database_connection import SchemaNotSupportedError
from dataherald.types import FineTuningRequest, GoldenSQL


def extract_the_schemas_from_sql(sql: str) -> list[str]:
    table_names = Parser(sql).tables
    schemas = []
    for table_name in table_names:
        if "." in table_name:
            schema = table_name.split(".")[0]
            schemas.append(schema.strip())
    return schemas


def filter_golden_records_based_on_schema(
    golden_sqls: list[GoldenSQL], schemas: list[str]
) -> list[GoldenSQL]:
    filtered_records = []
    if not schemas:
        return golden_sqls
    for record in golden_sqls:
        used_schemas = extract_the_schemas_from_sql(record.sql)
        for schema in schemas:
            if schema in used_schemas:
                filtered_records.append(record)
                break
    return filtered_records


def validate_finetuning_schema(
    finetuning_request: FineTuningRequest, db_connection: DatabaseConnection
):
    if finetuning_request.schemas:
        if not db_connection.schemas:
            raise SchemaNotSupportedError(
                "Schema not supported for this db",
                description=f"The {db_connection.id} db doesn't have schemas",
            )
        for schema in finetuning_request.schemas:
            if schema not in db_connection.schemas:
                raise SchemaNotSupportedError(
                    f"Schema {schema} not supported for this db",
                    description=f"The {db_connection.dialect} dialect doesn't support schema {schema}",
                )
