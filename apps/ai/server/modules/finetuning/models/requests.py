from typing import Any

from pydantic import BaseModel

from modules.finetuning.models.entities import BaseLLM


class FinetuningRequest(BaseModel):
    db_connection_id: str
    alias: str
    base_llm: BaseLLM
    golden_sqls: list[str] = []
    metadata: dict[str, Any] | None = {}
