import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, BaseSettings


class SSHSettings(BaseSettings):
    load_dotenv()

    enabled: bool
    host: str | None
    username: str | None
    password: str | None

    remote_host: str | None
    remote_db_name: str | None
    remote_db_password: str | None
    private_key_path: str | None
    private_key_password: str | None = None
    db_driver: str | None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class DatabaseConnection(BaseModel):
    load_dotenv()
    alias: str
    use_ssh: bool
    uri: str | None
    ssh_settings: SSHSettings | None = None
