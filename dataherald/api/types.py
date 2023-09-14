from dataherald.types import DBConnectionValidation


class Query(DBConnectionValidation):
    sql_query: str
