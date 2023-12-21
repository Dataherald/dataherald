from datetime import datetime

from pydantic import BaseModel, Extra


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


# TODO: find a better way to do this for all metadata
class DHDBConnectionMetadata(BaseModel):
    organization_id: str | None


class DBConnectionMetadata(BaseModel):
    dh_internal: DHDBConnectionMetadata | None

    class Config:
        extra = Extra.allow


class BaseDBConnection(BaseModel):
    id: str
    llm_api_key: str | None
    alias: str | None
    use_ssh: bool = False
    uri: str | None
    path_to_credentials_file: str | None
    ssh_settings: SSHSettings | None


class DBConnection(BaseDBConnection):
    metadata: DBConnectionMetadata | None
    created_at: datetime | None


class Driver(BaseModel):
    name: str | None
    driver: str
