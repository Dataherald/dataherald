from pydantic import BaseModel


class ColumnDescriptionRequest(BaseModel):
    name: str
    description: str


class TableDescriptionRequest(BaseModel):
    description: str | None
    columns: list[ColumnDescriptionRequest] | None
