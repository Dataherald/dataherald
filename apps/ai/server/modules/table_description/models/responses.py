from pydantic import BaseModel, Field

from modules.table_description.models.entities import BaseTableDescription


class TableDescriptionResponse(BaseTableDescription):
    id: str | None = Field(alias="_id")
    table_name: str


class BasicTableDescriptionResponse(BaseModel):
    id: str
    name: str | None
    columns: list[str] | None


class DatabaseDescriptionResponse(BaseModel):
    alias: str
    tables: list[BasicTableDescriptionResponse]
