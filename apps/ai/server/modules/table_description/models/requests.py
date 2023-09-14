from pydantic import BaseModel

from modules.table_description.models.entities import BaseTableDescription


class TableDescriptionRequest(BaseTableDescription):
    pass


class ScanRequest(BaseModel):
    db_connection_id: str
    table_names: list[str] | None
