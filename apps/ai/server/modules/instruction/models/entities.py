from typing import Any

from pydantic import BaseModel, Field


class BaseInstruction(BaseModel):
    instruction: str


class Instruction(BaseInstruction):
    id: Any = Field(alias="_id")
    db_connection_id: str
