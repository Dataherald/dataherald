from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class GoldenSQLSource(Enum):
    user_upload = "USER_UPLOAD"
    verified_query = "VERIFIED_QUERY"


class GoldenSQLRef(BaseModel):
    id: Any = Field(alias="_id")
    query_response_id: Any | None
    golden_sql_id: Any
    organization_id: Any
    source: str
    created_time: str


class GoldenSQL(BaseModel):
    id: Any = Field(alias="_id")
    question: str
    sql_query: str
    db_alias: str
