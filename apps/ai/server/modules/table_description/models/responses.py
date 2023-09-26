from pydantic import BaseModel, Extra

from modules.table_description.models.entities import BaseTableDescription, SchemaStatus


class TableDescriptionResponse(BaseTableDescription):
    id: str | None
    table_name: str
    status: str | None
    status: SchemaStatus
    last_schemas_sync: str | None

    class Config:
        extra = Extra.ignore


class BasicTableDescriptionResponse(BaseModel):
    id: str | None
    name: str | None
    columns: list[str] | None
    status: SchemaStatus
    last_schemas_sync: str | None


class DatabaseDescriptionResponse(BaseModel):
    alias: str
    tables: list[BasicTableDescriptionResponse]
