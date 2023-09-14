from typing import Any

from pydantic import BaseModel, Field


class ColumnDescription(BaseModel):
    name: str | None
    description: str | None


class BaseTableDescription(BaseModel):
    description: str | None
    columns: list[ColumnDescription] | None


class TableDescription(BaseTableDescription):
    id: Any = Field(alias="_id")
    table_name: str | None
