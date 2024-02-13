from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra

from utils.validation import ObjectIdString


class GoldenSQLSource(str, Enum):
    USER_UPLOAD = "USER_UPLOAD"
    VERIFIED_QUERY = "VERIFIED_QUERY"


class DHGoldenSQLMetadata(BaseModel):
    prompt_id: ObjectIdString | None
    organization_id: ObjectIdString | None
    source: GoldenSQLSource | None
    display_id: str | None


class GoldenSQLMetadata(BaseModel):
    dh_internal: DHGoldenSQLMetadata | None

    class Config:
        extra = Extra.allow


class BaseGoldenSQL(BaseModel):
    db_connection_id: ObjectIdString
    prompt_text: str
    sql: str


class GoldenSQL(BaseGoldenSQL):
    id: ObjectIdString
    created_at: datetime | None
    metadata: GoldenSQLMetadata | None


class AggrGoldenSQL(GoldenSQL):
    db_connection_alias: str | None
