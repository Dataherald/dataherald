from pydantic import BaseModel

from modules.queries.models.entities import (
    QueryStatus,
    User,
)


class QueryResponse(BaseModel):
    id: str
    user: User
    question: str
    nl_response: str
    sql_query: str
    question_date: str
    last_updated: str
    status: QueryStatus
    evaluation_score: float
