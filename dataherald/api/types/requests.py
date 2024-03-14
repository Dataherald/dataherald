from pydantic import BaseModel

from dataherald.types import LLMConfig


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    metadata: dict | None


class SQLGenerationRequest(BaseModel):
    finetuning_id: str | None
    low_latency_mode: bool = False
    llm_config: LLMConfig | None
    evaluate: bool = False
    sql: str | None
    metadata: dict | None


class StreamSQLGenerationRequest(BaseModel):
    finetuning_id: str | None
    low_latency_mode: bool = False
    llm_config: LLMConfig | None
    metadata: dict | None


class PromptSQLGenerationRequest(SQLGenerationRequest):
    prompt: PromptRequest


class StreamPromptSQLGenerationRequest(StreamSQLGenerationRequest):
    prompt: PromptRequest


class NLGenerationRequest(BaseModel):
    llm_config: LLMConfig | None
    max_rows: int = 100
    metadata: dict | None


class NLGenerationsSQLGenerationRequest(NLGenerationRequest):
    sql_generation: SQLGenerationRequest


class PromptSQLGenerationNLGenerationRequest(NLGenerationRequest):
    sql_generation: PromptSQLGenerationRequest


class UpdateMetadataRequest(BaseModel):
    metadata: dict | None
