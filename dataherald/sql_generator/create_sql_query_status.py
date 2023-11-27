import csv
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import text

from dataherald.config import Settings
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import Response, SQLQueryResult
from dataherald.utils.s3 import S3


def format_error_message(response: Response, error_message: str) -> Response:
    # Remove the complete query
    if error_message.find("[") > 0 and error_message.find("]") > 0:
        error_message = (
            error_message[0 : error_message.find("[")]
            + error_message[error_message.rfind("]") + 1 :]
        )
    response.sql_generation_status = "INVALID"
    response.response = ""
    response.sql_query_result = None
    response.error_message = error_message
    return response


def create_csv_file(
    generate_csv: bool,
    columns: list,
    rows: list,
    response: Response,
    database_connection: DatabaseConnection | None = None,
):
    if generate_csv:
        file_location = f"tmp/{str(uuid.uuid4())}.csv"
        with open(file_location, "w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(rows[0].keys())
            for row in rows:
                writer.writerow(row.values())
        if Settings().only_store_csv_files_locally:
            response.csv_file_path = file_location
        else:
            s3 = S3()
            response.csv_file_path = s3.upload(
                file_location, database_connection.file_storage
            )
    response.sql_query_result = SQLQueryResult(columns=columns, rows=rows)


def create_sql_query_status(
    db: SQLDatabase,
    query: str,
    response: Response,
    top_k: int = None,
    generate_csv: bool = False,
    database_connection: DatabaseConnection | None = None,
) -> Response:
    """Find the sql query status and populate the fields sql_query_result, sql_generation_status, and error_message"""
    if query == "":
        response.sql_generation_status = "INVALID"
        response.response = ""
        response.sql_query_result = None
        response.error_message = None
    else:
        try:
            query = db.parser_to_filter_commands(query)
            with db._engine.connect() as connection:
                execution = connection.execute(text(query))
                columns = execution.keys()
                if top_k:
                    result = execution.fetchmany(top_k)
                else:
                    result = execution.fetchall()
            if len(result) == 0:
                response.sql_query_result = None
            else:
                columns = [item for item in columns]  # noqa: C416
                rows = []
                for row in result:
                    modified_row = {}
                    for key, value in zip(row.keys(), row, strict=True):
                        if type(value) in [
                            date,
                            datetime,
                        ]:  # Check if the value is an instance of datetime.date
                            modified_row[key] = str(value)
                        elif (
                            type(value) is Decimal
                        ):  # Check if the value is an instance of decimal.Decimal
                            modified_row[key] = float(value)
                        else:
                            modified_row[key] = value
                    rows.append(modified_row)

                create_csv_file(
                    generate_csv,
                    columns,
                    rows,
                    response,
                    database_connection,
                )

            response.sql_generation_status = "VALID"
            response.error_message = None
        except SQLInjectionError as e:
            raise SQLInjectionError(
                "Sensitive SQL keyword detected in the query."
            ) from e
        except Exception as e:
            response = format_error_message(response, str(e))

    return response
