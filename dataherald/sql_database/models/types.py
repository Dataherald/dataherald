import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, BaseSettings


class SSHSettings(BaseSettings):
    load_dotenv()

    host: str | None = os.environ.get("SSH_HOST")
    username: str | None = os.environ.get("SSH_USERNAME")
    password: str | None = os.environ.get("SSH_PASSWORD")

    remote_host: str | None = os.environ.get("SSH_REMOTE_HOST")
    remote_db_name: str | None = os.environ.get("SSH_REMOTE_DB_NAME")
    remote_db_password: str | None = os.environ.get("SSH_REMOTE_DB_PASSWORD")
    private_key_path: str | None = os.environ.get("SSH_PRIVATE_KEY_PATH")
    private_key_password: str | None = os.environ.get("SSH_PRIVATE_KEY_PASSWORD")
    db_driver: str | None = os.environ.get("SSH_DB_DRIVER")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class DatabaseConnection(BaseModel):
    load_dotenv()
    alias: str
    use_ssh: bool = os.environ.get("SSH_ENABLED")
    uri: str | None = os.environ.get("DATABASE_URI")
    ssh_settings: SSHSettings | None = None
