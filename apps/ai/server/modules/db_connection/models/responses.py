from pydantic import BaseModel


class DatabaseResponse(BaseModel):
    alias: str
