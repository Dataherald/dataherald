from typing import Any

from pydantic import BaseModel, Field


class SSHSettings(BaseModel):
    db_name: str | None
    host: str | None
    username: str | None
    password: str | None

    remote_host: str | None
    remote_db_name: str | None
    remote_db_password: str | None
    private_key_password: str | None
    db_driver: str | None


class BaseDBConnection(BaseModel):
    alias: str | None
    use_ssh: bool = False

    path_to_credentials_file: str | None
    ssh_settings: SSHSettings | None


class DBConnection(BaseDBConnection):
    id: Any = Field(alias="_id")
    uri: str | None
    llm_api_key: str | None


class DBConnectionRef(BaseModel):
    id: Any = Field(alias="_id")
    db_connection_id: Any
    organization_id: Any


class Driver(BaseModel):
    name: str | None
    driver: str
