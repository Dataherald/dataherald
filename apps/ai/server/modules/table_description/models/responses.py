from pydantic import BaseModel

from modules.table_description.models.entities import BaseTableDescription, SchemaStatus


class TableDescriptionResponse(BaseTableDescription):
    id: str
    table_name: str
    schemas_status: SchemaStatus | None
    last_schemas_sync: str | None


class BasicTableDescriptionResponse(BaseModel):
    id: str
    name: str | None
    columns: list[str] | None
    schemas_status: SchemaStatus | None
    last_schemas_sync: str | None


class DatabaseDescriptionResponse(BaseModel):
    alias: str
    tables: list[BasicTableDescriptionResponse]
