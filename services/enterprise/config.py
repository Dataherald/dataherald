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
USAGE_COL = "usages"
CREDIT_COL = "credits"

SAMPLE_DATABASE_COL = "sample_databases"


class Settings(BaseSettings):
    load_dotenv()

    engine_url: str = os.environ.get("ENGINE_URL")
    default_engine_timeout: int = os.environ.get("DEFAULT_ENGINE_TIMEOUT")
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
    s3_bucket_name: str = os.environ.get("S3_BUCKET_NAME", "k2-core")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class AuthSettings(BaseSettings):
    load_dotenv()

    auth_disabled: bool = os.environ.get("AUTH_DISABLED", False)

    auth0_domain: str = os.environ.get("AUTH0_DOMAIN")
    auth0_algorithms: str = os.environ.get("AUTH0_ALGORITHMS", "RS256")
    auth0_audience: str = os.environ.get("AUTH0_API_AUDIENCE")
    auth0_issuer: str = os.environ.get("AUTH0_ISSUER_BASE_URL")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class SSHSettings(BaseSettings):
    load_dotenv()
    private_key_password: str = os.environ.get("SSH_PRIVATE_KEY_PASSWORD")
    path_to_credentials_file: str = os.environ.get("SSH_PATH_TO_CREDENTIAL_FILE")

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


class InvoiceSettings(BaseSettings):
    load_dotenv()

    stripe_disabled: bool = os.environ.get("STRIPE_DISABLED", False)
    stripe_api_key: str = os.environ.get("STRIPE_API_KEY", None)
    stripe_webhook_secret: str = os.environ.get("STRIPE_WEBHOOK_SECRET", None)

    sql_generation_price_id: str = os.environ.get(
        "SQL_GENERATION_PRICE_ID", "price_1OdyLiEohyIdoJ6Sl0teIo81"
    )
    finetuning_gpt_35_price_id: str = os.environ.get(
        "FINETUNING_GPT_35_PRICE_ID", "price_1OegSUEohyIdoJ6SVSIhvjrX"
    )
    finetuning_gpt_4_price_id: str = os.environ.get(
        "FINETUNING_GPT_4_PRICE_ID", "price_1OegR6EohyIdoJ6SLF0XT40D"
    )
    # in the future we can store the cost in the db and update it with webhooks
    sql_generation_cost: int = os.environ.get("SQL_GENERATION_COST", 90)
    finetuning_gpt_35_cost: int = os.environ.get("FINETUNING_GPT_35_COST", 50)
    finetuning_gpt_4_cost: int = os.environ.get("FINETUNING_GPT_4_COST", 300)

    default_hard_spending_limit: int = os.environ.get("HARD_SPENDING_LIMIT", 100000)
    default_spending_limit: int = os.environ.get("DEFAULT_SPENDING_LIMIT", 30000)
    signup_credits: int = os.environ.get("SIGNUP_CREDITS", 5000)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


settings = Settings()
db_settings = DBSettings()
auth_settings = AuthSettings()
slack_settings = SlackSettings()
aws_s3_settings = AWSS3Settings()
analytic_settings = AnalyticSettings()
ssh_settings = SSHSettings()
invoice_settings = InvoiceSettings()
