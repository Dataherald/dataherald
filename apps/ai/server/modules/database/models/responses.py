from pydantic import BaseModel


class ScannedDBTable(BaseModel):
    id: str
    name: str
    columns: list[str]


class ScannedDBResponse(BaseModel):
    db_alias: str
    tables: list[ScannedDBTable]
