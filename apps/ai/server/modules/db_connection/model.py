from pydantic import BaseModel


class TableInfo(BaseModel):
    name: str
    # probably not needed?
    last_updated: str


class DatabaseResponse(BaseModel):
    name: str
    source: str
    table_count: int
    tables: list[TableInfo]


class DatabasesResponse(BaseModel):
    count: int
    databases: list[DatabaseResponse]
