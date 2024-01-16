from pydantic import BaseModel


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    metadata: dict | None


class SQLGenerationRequest(BaseModel):
    finetuning_id: str | None
    evaluate: bool = False
    sql: str | None
    metadata: dict | None


class PromptSQLGenerationRequest(SQLGenerationRequest):
    prompt: PromptRequest


class NLGenerationRequest(BaseModel):
    max_rows: int = 100
    metadata: dict | None


class NLGenerationsSQLGenerationRequest(NLGenerationRequest):
    sql_generation: SQLGenerationRequest


class PromptSQLGenerationNLGenerationRequest(NLGenerationRequest):
    sql_generation: PromptSQLGenerationRequest


class UpdateMetadataRequest(BaseModel):
    metadata: dict | None
