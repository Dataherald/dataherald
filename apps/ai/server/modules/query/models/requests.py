from pydantic import BaseModel

from modules.query.models.entities import QueryStatus


class QueryEditRequest(BaseModel):
    sql_query: str
    query_status: QueryStatus | None


class SQLQueryRequest(BaseModel):
    sql_query: str
