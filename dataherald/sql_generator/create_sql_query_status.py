from datetime import date
from decimal import Decimal

from sqlalchemy import text

from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.types import NLQueryResponse, SQLQueryResult


def create_sql_query_status(
    db: SQLDatabase, query: str, response: NLQueryResponse
) -> NLQueryResponse:
    """Find the sql query status and populate the fields sql_query_result, sql_generation_status, and error_message"""
    if query == "":
        response.sql_generation_status = "NONE"
        response.sql_query_result = None
        response.error_message = None
    else:
        try:
            query = db.parser_to_filter_commands(query)
            with db._engine.connect() as connection:
                execution = connection.execute(text(query))
                columns = execution.keys()
                result = execution.fetchall()
            if len(result) == 0:
                response.sql_query_result = None
            else:
                columns = [item for item in columns]  # noqa: C416
                rows = []
                for row in result:
                    modified_row = {}
                    for key, value in zip(row.keys(), row, strict=True):
                        if (
                            type(value) is date
                        ):  # Check if the value is an instance of datetime.date
                            modified_row[key] = str(value)
                        elif (
                            type(value) is Decimal
                        ):  # Check if the value is an instance of decimal.Decimal
                            modified_row[key] = float(value)
                        else:
                            modified_row[key] = value
                    rows.append(modified_row)
                response.sql_query_result = SQLQueryResult(columns=columns, rows=rows)
            response.sql_generation_status = "VALID"
            response.error_message = None
        except SQLInjectionError as e:
            raise SQLInjectionError(
                "Sensitive SQL keyword detected in the query."
            ) from e
        except Exception as e:
            response.sql_generation_status = "INVALID"
            response.sql_query_result = None
            response.error_message = str(e)
    return response
