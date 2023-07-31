import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseSettings

DB_CONNECTION_COL = "database_connection"
QUESTION_COL = "nl_question"
QUERY_RESPONSE_COL = "nl_query_response"
QUERY_RESPONSE_REF_COL = "nl_query_response_ref"


class Settings(BaseSettings):
    load_dotenv()

    k2_core_url: str = os.environ.get("K2_CORE_URL")
    default_k2_core_timeout: int = os.environ.get("DEFAULT_TIMEOUT")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class DBSettings(BaseSettings):
    load_dotenv()

    mongodb_uri: str = os.environ.get("MONGO_URI")
    mongodb_db_name: str = os.environ.get("MONGODB_DB_NAME")

    db_alias: str = os.environ.get("DB_ALIAS", "v2_real_estate")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


settings = Settings()
dbsettings = DBSettings()
