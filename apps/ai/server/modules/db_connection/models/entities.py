from pydantic import BaseModel


class TableInfo(BaseModel):
    name: str
    # probably not needed?
    last_updated: str
