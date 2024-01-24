from datetime import datetime

from pydantic import BaseModel, Extra


class SSHSettings(BaseModel):
    host: str | None
    username: str | None
    password: str | None


# TODO: find a better way to do this for all metadata
class DHDBConnectionMetadata(BaseModel):
    organization_id: str | None


class DBConnectionMetadata(BaseModel):
    dh_internal: DHDBConnectionMetadata | None

    class Config:
        extra = Extra.allow


class BaseDBConnection(BaseModel):
    alias: str
    use_ssh: bool = False
    connection_uri: str
    ssh_settings: SSHSettings | None
    metadata: DBConnectionMetadata | None


class InternalSSHSettings(SSHSettings):
    private_key_password: str | None


class DBConnection(BaseDBConnection):
    id: str | None
    created_at: datetime | None
    path_to_credentials_file: str | None
    ssh_settings: InternalSSHSettings | None


class Driver(BaseModel):
    name: str | None
    driver: str
