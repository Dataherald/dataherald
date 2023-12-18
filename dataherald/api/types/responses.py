from pydantic import BaseModel


class PromptResponse(BaseModel):
    id: str
    text: str
    db_connection_id: str
    created_at: str
    metadata: dict | None


class SQLGenerationResponse(BaseModel):
    id: str
    prompt_id: str
    model: str | None
    status: str
    completed_at: str
    sql: str | None
    tokens_used: int | None
    confidence_score: float | None
    error: str | None
    created_at: str
    metadata: dict | None


class NLGenerationResponse(BaseModel):
    id: str
    sql_generation_id: str
    nl_answer: str
    created_at: str
    metadata: dict | None
