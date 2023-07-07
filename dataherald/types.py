from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class NLQuery(BaseModel):
    id: Any
    question: str


class NLQueryResponse(BaseModel):
    id: Any
    nl_question_id: Any
    nl_response: str | None = None
    intermediate_steps: list[str] | None = None
    sql_query: str
    exec_time: float | None = None
    golden_record: bool = False
    #date_entered: datetime = datetime.now()


class DataDefinitionType(Enum):
    GOLDEN_SQL = "GOLDEN_SQL"
    BUSINESS_CONTEXT = "BUSINESS_CONTEXT"


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"
