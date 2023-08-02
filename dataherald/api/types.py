from pydantic import BaseModel


class Query(BaseModel):
    sql_statement: str
    db_alias: str
