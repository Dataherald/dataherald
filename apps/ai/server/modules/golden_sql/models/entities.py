from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra


class GoldenSQLSource(str, Enum):
    USER_UPLOAD = "USER_UPLOAD"
    VERIFIED_QUERY = "VERIFIED_QUERY"


class DHGoldenSQLMetadata(BaseModel):
    prompt_id: str | None
    organization_id: str | None
    source: GoldenSQLSource | None
    display_id: str | None


class GoldenSQLMetadata(BaseModel):
    dh_internal: DHGoldenSQLMetadata | None

    class Config:
        extra = Extra.allow


class BaseGoldenSQL(BaseModel):
    db_connection_id: str
    prompt_text: str
    sql: str


class GoldenSQL(BaseGoldenSQL):
    id: str
    created_at: datetime | None
    metadata: GoldenSQLMetadata | None


class AggrGoldenSQL(GoldenSQL):
    db_connection_alias: str | None
