import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseSettings

PROMPT_COL = "prompts"
SQL_GENERATION_COL = "sql_generations"
NL_GENERATION_COL = "nl_generations"

DATABASE_CONNECTION_COL = "database_connections"
GOLDEN_SQL_COL = "golden_sqls"
TABLE_DESCRIPTION_COL = "table_descriptions"
INSTRUCTION_COL = "instructions"
FINETUNING_COL = "finetunings"

USER_COL = "users"
ORGANIZATION_COL = "organizations"
KEY_COL = "keys"


class Settings(BaseSettings):
    load_dotenv()

    engine_url: str = os.environ.get("K2_CORE_URL")
    default_engine_timeout: int = os.environ.get("DEFAULT_K2_TIMEOUT")
    encrypt_key: str = os.environ.get("ENCRYPT_KEY")
    api_key_salt: str = os.environ.get("API_KEY_SALT")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class DBSettings(BaseSettings):
    load_dotenv()

    mongodb_uri: str = os.environ.get("MONGO_URI")
    mongodb_db_name: str = os.environ.get("MONGODB_DB_NAME")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class AWSS3Settings(BaseSettings):
    load_dotenv()

    s3_aws_access_key_id: str = os.environ.get("S3_AWS_ACCESS_KEY_ID")
    s3_aws_secret_access_key: str = os.environ.get("S3_AWS_SECRET_ACCESS_KEY")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class AuthSettings(BaseSettings):
    load_dotenv()

    auth0_domain: str = os.environ.get("AUTH0_DOMAIN")
    auth0_algorithms: str = os.environ.get("AUTH0_ALGORITHMS", "RS256")
    auth0_audience: str = os.environ.get("AUTH0_API_AUDIENCE")
    auth0_issuer: str = os.environ.get("AUTH0_ISSUER")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class SlackSettings(BaseSettings):
    load_dotenv()

    slack_bot_access_token: str = os.environ.get("SLACK_BOT_ACCESS_TOKEN", None)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class AnalyticSettings(BaseSettings):
    load_dotenv()

    posthog_api_key: str = os.environ.get("POSTHOG_API_KEY", "")
    posthog_host: str = os.environ.get("POSTHOG_HOST", None)
    posthog_disabled: bool = os.environ.get("POSTHOG_DISABLED", False)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


settings = Settings()
db_settings = DBSettings()
auth_settings = AuthSettings()
slack_settings = SlackSettings()
aws_s3_settings = AWSS3Settings()
analytic_settings = AnalyticSettings()
