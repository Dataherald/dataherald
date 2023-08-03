from pydantic import BaseModel


class TableInfo(BaseModel):
    name: str
    last_updated: str
