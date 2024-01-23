from typing import Any

from pydantic import BaseModel

from modules.finetuning.models.entities import BaseLLM


class FinetuningRequest(BaseModel):
    db_connection_id: str
    alias: str
    base_llm: BaseLLM | None
    golden_records: list[str] | None = None
    metadata: dict[str, Any] | None = {}
