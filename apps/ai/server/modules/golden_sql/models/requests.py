from pydantic import BaseModel


class GoldenSQLRequest(BaseModel):
    question: str
    sql_query: str
    db_alias: str
