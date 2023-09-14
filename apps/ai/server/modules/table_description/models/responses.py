from pydantic import Field

from modules.table_description.models.entities import BaseTableDescription


class TableDescriptionResponse(BaseTableDescription):
    id: str | None = Field(alias="_id")
    table_name: str
