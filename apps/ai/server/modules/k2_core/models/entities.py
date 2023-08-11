from enum import Enum

from pydantic import BaseModel, Field


class NLQuery(BaseModel):
    id: str | None = Field(alias="_id")
    question: str


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]


class SQLGenerationStatus(Enum):
    none = "NONE"
    invalid = "INVALID"
    valid = "VALID"
