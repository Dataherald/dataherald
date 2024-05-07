from pydantic import BaseModel, validator
from sql_metadata import Parser

from dataherald.types import LLMConfig


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    schemas: list[str] | None
    metadata: dict | None


class SQLGenerationRequest(BaseModel):
    finetuning_id: str | None
    low_latency_mode: bool = False
    llm_config: LLMConfig | None
    evaluate: bool = False
    sql: str | None
    metadata: dict | None

    @validator("sql")
    def validate_model_name(cls, v: str | None):
        try:
            Parser(v).tables  # noqa: B018
        except Exception as e:
            raise ValueError(f"SQL {v} is malformed. Please check the syntax.") from e
        return v


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
