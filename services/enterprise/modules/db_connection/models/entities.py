from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra

from utils.validation import ObjectIdString


class DatabaseDialects(str, Enum):
    POSTGRES = "postgresql"
    MYSQL = "mysql"
    MSSQL = "mssql"
    DATABRICKS = "databricks"
    SNOWFLAKE = "snowflake"
    CLICKHOUSE = "clickhouse"
    AWSATHENA = "awsathena"
    DUCKDB = "duckdb"
    BIGQUERY = "bigquery"
    SQLITE = "sqlite"
    REDSHIFT = "redshift"


class SSHSettings(BaseModel):
    host: str | None
    username: str | None
    password: str | None
    port: str | None


# TODO: find a better way to do this for all metadata
class DHDBConnectionMetadata(BaseModel):
    organization_id: ObjectIdString | None


class DBConnectionMetadata(BaseModel):
    dh_internal: DHDBConnectionMetadata | None

    class Config:
        extra = Extra.allow


class BaseDBConnection(BaseModel):
    alias: str
    use_ssh: bool = False
    connection_uri: str
    ssh_settings: SSHSettings | None
    schemas: list[str] | None
    metadata: DBConnectionMetadata | None


class InternalSSHSettings(SSHSettings):
    private_key_password: str | None


class DBConnection(BaseDBConnection):
    id: ObjectIdString | None
    llm_api_key: str | None = None
    created_at: datetime | None
    path_to_credentials_file: str | None
    ssh_settings: InternalSSHSettings | None
    dialect: DatabaseDialects | None
