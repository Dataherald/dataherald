from pydantic import BaseModel


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    metadata: dict | None


class SQLGenerationRequest(BaseModel):
    model: str | None
    evaluate: bool = False
    sql: str | None
    metadata: dict | None


class NLGenerationRequest(BaseModel):
    max_rows: int
    metadata: dict | None
