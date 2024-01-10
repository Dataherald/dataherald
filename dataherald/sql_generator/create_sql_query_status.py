from sqlalchemy import text

from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.types import SQLGeneration


def format_error_message(
    sql_generation: SQLGeneration, error_message: str
) -> SQLGeneration:
    # Remove the complete query
    if error_message.find("[") > 0 and error_message.find("]") > 0:
        error_message = (
            error_message[0 : error_message.find("[")]
            + error_message[error_message.rfind("]") + 1 :]
        )
    sql_generation.status = "INVALID"
    sql_generation.error = error_message
    return sql_generation


def create_sql_query_status(
    db: SQLDatabase,
    query: str,
    sql_generation: SQLGeneration,
) -> SQLGeneration:
    """Find the sql query status and populate the fields sql_query_result, sql_generation_status, and error_message"""
    if query == "":
        sql_generation.status = "INVALID"
        sql_generation.error = "Sorry, we couldn't generate an SQL from your prompt"
    else:
        try:
            query = db.parser_to_filter_commands(query)
            with db._engine.connect() as connection:
                connection.execute(text(query))
            sql_generation.status = "VALID"
            sql_generation.error = None
        except SQLInjectionError as e:
            raise SQLInjectionError(
                "Sensitive SQL keyword detected in the query."
            ) from e
        except Exception as e:
            sql_generation = format_error_message(sql_generation, str(e))
    return sql_generation
