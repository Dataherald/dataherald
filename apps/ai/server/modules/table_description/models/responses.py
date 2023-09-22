from pydantic import BaseModel

from modules.table_description.models.entities import BaseTableDescription


class TableDescriptionResponse(BaseTableDescription):
    id: str
    table_name: str


class BasicTableDescriptionResponse(BaseModel):
    id: str
    name: str | None
    columns: list[str] | None


class DatabaseDescriptionResponse(BaseModel):
    alias: str
    tables: list[BasicTableDescriptionResponse]
