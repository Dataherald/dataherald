from typing import Any

from pydantic import BaseModel

from modules.finetuning.models.entities import BaseLLM


class FinetuningRequest(BaseModel):
    db_connection_id: str
    base_llm: BaseLLM
    golden_records: list[str] | None = None
    metadata: dict[str, Any] | None = {}
