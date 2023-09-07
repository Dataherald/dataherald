from dataherald.types import DBConnectionValidation


class Query(DBConnectionValidation):
    sql_statement: str
