from pydantic import BaseModel


class QueryResponse(BaseModel):
    query_id: str
    user: str
    question: str
    answer: str
    created_at: str
    confidence: int
    status: str


class QueriesReponse(BaseModel):
    limit: int
    skip: int
    order: str
    queries: list[QueryResponse]
