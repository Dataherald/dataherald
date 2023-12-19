from pydantic import BaseModel


class Query(BaseModel):
    max_rows: int = 100
    metadata: dict | None
