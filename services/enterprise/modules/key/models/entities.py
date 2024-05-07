from datetime import datetime

from pydantic import BaseModel

from utils.validation import ObjectIdString


class UnknownKeyError(Exception):
    def __init__(self, key_hash: str):
        print(f"Key with hash {key_hash}  does not exist")


class BaseKey(BaseModel):
    id: ObjectIdString | None
    name: str | None
    organization_id: ObjectIdString
    created_at: datetime = datetime.now()
    key_preview: str | None


class APIKey(BaseKey):
    key_hash: bytes
