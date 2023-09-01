from typing import Any

from pydantic import BaseModel, BaseSettings, validator

from dataherald.utils.encrypt import FernetEncrypt


class SSHSettings(BaseSettings):
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

    @validator(
        "password", "remote_db_password", "private_key_password", pre=True, always=True
    )
    def encrypt(cls, value: str):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
            return value
        except Exception:
            return fernet_encrypt.encrypt(value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class DatabaseConnection(BaseModel):
    id: Any
    alias: str
    use_ssh: bool = False
    uri: str | None
    path_to_credentials_file: str | None
    ssh_settings: SSHSettings | None = None

    @validator("uri", pre=True, always=True)
    def set_uri_without_ssh(cls, v, values):
        if values["use_ssh"] and v:
            raise ValueError("When use_ssh is True don't set uri")
        if not values["use_ssh"] and not v:
            raise ValueError("When use_ssh is False set uri")
        return v

    @validator("uri", pre=True, always=True)
    def encrypt(cls, value: str):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
            return value
        except Exception:
            return fernet_encrypt.encrypt(value)
