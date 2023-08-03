from enum import Enum

from pydantic import BaseModel, BaseSettings, Field


class NLQuery(BaseModel):
    id: str | None = Field(alias="_id")
    question: str


class DataDefinitionType(Enum):
    GOLDEN_SQL = "GOLDEN_SQL"
    BUSINESS_CONTEXT = "BUSINESS_CONTEXT"


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"


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


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]


class SQLGenerationStatus(Enum):
    none = "NONE"
    invalid = "INVALID"
    valid = "VALID"
