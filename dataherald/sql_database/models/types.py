import os
from typing import Any

from pydantic import BaseModel, BaseSettings, Extra, validator

from dataherald.utils.encrypt import FernetEncrypt


class LLMCredentials(BaseSettings):
    organization_id: str | None
    api_key: str | None

    @validator("api_key", "organization_id", pre=True, always=True)
    def encrypt(cls, value: str):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
            return value
        except Exception:
            return fernet_encrypt.encrypt(value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class FileStorage(BaseModel):
    name: str
    access_key_id: str
    secret_access_key: str
    region: str | None
    bucket: str

    class Config:
        extra = Extra.ignore

    @validator("access_key_id", "secret_access_key", pre=True, always=True)
    def encrypt(cls, value: str):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
            return value
        except Exception:
            return fernet_encrypt.encrypt(value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class SSHSettings(BaseSettings):
    db_name: str | None
    host: str | None
    username: str | None
    password: str | None
    remote_host: str | None
    remote_db_name: str | None
    remote_db_password: str | None
    private_key_password: str | None
    db_driver: str | None

    class Config:
        extra = Extra.ignore

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
    id: str | None
    alias: str
    use_ssh: bool = False
    uri: str | None
    path_to_credentials_file: str | None
    llm_api_key: str | None = None
    ssh_settings: SSHSettings | None = None
    file_storage: FileStorage | None = None

    @validator("uri", pre=True, always=True)
    def set_uri_without_ssh(cls, v, values):
        if values["use_ssh"] and v:
            raise ValueError("When use_ssh is True don't set uri")
        if not values["use_ssh"] and not v:
            raise ValueError("When use_ssh is False set uri")
        return v

    @validator("uri", "llm_api_key", pre=True, always=True)
    def encrypt(cls, value: str):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
            return value
        except Exception:
            return fernet_encrypt.encrypt(value)

    def decrypt_api_key(self):
        if self.llm_api_key is not None and self.llm_api_key != "":
            fernet_encrypt = FernetEncrypt()
            return fernet_encrypt.decrypt(self.llm_api_key)
        return os.environ.get("OPENAI_API_KEY")
