from enum import Enum

from posthog import Posthog
from pydantic import BaseModel

from config import analytic_settings


class EventName(str, Enum):
    organization_created = "organization_created"
    user_invited = "user_invited"
    golden_sql_created = "golden_sql_created"
    db_connection_created = "db_connection_created"
    finetuning_created = "finetuning_created"
    sql_generation_created = "sql_generation_created"
    sql_generation_updated = "sql_generation_updated"
    usage_recorded = "usage_recorded"


class Event(BaseModel):
    id: str | None
    organization_id: str | None


class DBConnectionEvent(Event):
    database_type: str | None


class FinetuningEvent(Event):
    db_connection_id: str | None
    db_connection_alias: str | None
    model_provider: str | None
    model_name: str | None
    golden_sql_quantity: int | None


class GoldenSQLEvent(Event):
    quantity: int | None


class OrganizationEvent(Event):
    name: str | None
    owner: str | None


class SQLGenerationEvent(Event):
    source: str | None
    status: str | None
    confidence_score: float | None
    execution_time: int | None


class SQLGenerationUpdatedEvent(Event):
    generation_status: str | None
    confidence_score: float | None
    sql_modified: bool | None


class UserEvent(Event):
    email: str | None
    name: str | None


class UsageEvent(Event):
    type: str | None
    cost: float | None


class EventType(BaseModel):
    db_connection_event = DBConnectionEvent
    finetuning_event = FinetuningEvent
    golden_sql_event = GoldenSQLEvent
    organization_event = OrganizationEvent
    sql_generation_event = SQLGenerationEvent
    sql_generation_updated_event = SQLGenerationUpdatedEvent
    user_event = UserEvent
    usage_event = UsageEvent


class Properties(BaseModel):
    id: str | None


class UserProperties(Properties):
    email: str | None
    name: str | None
    organization_id: str | None
    organization_name: str | None


class OrganizationProperties(Properties):
    name: str | None
    owner: str | None


class Analytics:
    def __init__(self):
        self.posthog = Posthog(
            analytic_settings.posthog_api_key, host=analytic_settings.posthog_host
        )
        if analytic_settings.posthog_disabled:
            self.posthog.disabled = True

    def track(self, user_id: str, event: str, properties: Event):
        self.posthog.capture(
            user_id,
            event,
            properties=properties.dict(),
        )

    def identify(self, user_id: str, properties: Properties):
        self.posthog.identify(
            user_id,
            properties=properties.dict(),
        )

    def track_error(
        self,
        user_id: str,
        path: str,
    ):
        self.track(
            user_id,
            "engine_error",
            {
                "path": path,
            },
        )
