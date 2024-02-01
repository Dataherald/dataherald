from pydantic import BaseModel


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    metadata: dict | None


class LLMConfig(BaseModel):
    llm_name: str = "gpt-4-turbo-preview"
    api_base: str | None = None


class SQLGenerationRequest(BaseModel):
    finetuning_id: str | None
    low_latency_mode: bool = False
    llm_config: LLMConfig = LLMConfig()
    evaluate: bool = False
    sql: str | None
    metadata: dict | None


class PromptSQLGenerationRequest(SQLGenerationRequest):
    prompt: PromptRequest


class NLGenerationRequest(BaseModel):
    llm_config: LLMConfig
    max_rows: int = 100
    metadata: dict | None


class NLGenerationsSQLGenerationRequest(NLGenerationRequest):
    sql_generation: SQLGenerationRequest


class PromptSQLGenerationNLGenerationRequest(NLGenerationRequest):
    sql_generation: PromptSQLGenerationRequest


class UpdateMetadataRequest(BaseModel):
    metadata: dict | None
