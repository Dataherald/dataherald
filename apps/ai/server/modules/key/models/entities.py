from datetime import datetime

from pydantic import BaseModel


class UnknownKeyError(Exception):
    def __init__(self, key_hash: str):
        print(f"Key with hash {key_hash}  does not exist")


class BaseKey(BaseModel):
    id: str | None
    name: str | None
    organization_id: str
    created_at: datetime | None
    key_preview: str | None


class APIKey(BaseKey):
    key_hash: bytes
