from enum import Enum
from typing import Any

from pydantic import BaseModel, BaseSettings, Field, confloat

"""
from dataherald.dataherald.types import DataDefinitionType, NLQueryResponse
from dataherald.dataherald.eval import Evaluation
from dataherald.dataherald.sql_database.models.types import SSHSettings
"""

### TODO use dataherald as package and import these models instead ###


class NLQuery(BaseModel):
    id: str | None = Field(alias="_id")
    question: str


class NLQueryResponse(BaseModel):
    id: str | None = Field(alias="_id")
    nl_question_id: Any
    nl_response: str | None = None
    intermediate_steps: list[str] | None = None
    sql_query: str
    exec_time: float | None = None
    golden_record: bool = False
    # date_entered: datetime = datetime.now() add this later


class DataDefinitionType(Enum):
    GOLDEN_SQL = "GOLDEN_SQL"
    BUSINESS_CONTEXT = "BUSINESS_CONTEXT"


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"


class Evaluation(BaseModel):
    id: str | None = Field(alias="_id")
    question_id: str | None = Field(alias="q_id")
    answer_id: str | None = Field(alias="a_id")
    score: confloat(ge=0, le=1) = 0.5


class SSHSettings(BaseSettings):
    host: str | None
    username: str | None
    password: str | None

    remote_host: str | None
    remote_db_name: str | None
    remote_db_password: str | None
    private_key_path: str | None
    private_key_password: str | None
    db_driver: str | None
