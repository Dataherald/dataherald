from pydantic import BaseModel


class ColumnDescriptionRequest(BaseModel):
    name: str
    description: str


class TableDescriptionRequest(BaseModel):
    table_name: str
    description: str | None
    columns: list[ColumnDescriptionRequest] | None


class ScanRequest(BaseModel):
    db_alias: str
    table_name: str


class SSHSettings(BaseModel):
    db_name: str | None
    host: str | None
    username: str | None
    password: str | None

    remote_host: str | None
    remote_db_name: str | None
    remote_db_password: str | None
    private_key_path: str | None
    private_key_password: str | None
    db_driver: str | None


class DatabaseConnectionRequest(BaseModel):
    db_alias: str | None
    use_ssh: bool = False
    connection_uri: str | None
    path_to_credentials_file: str | None
    ssh_settings: SSHSettings | None
