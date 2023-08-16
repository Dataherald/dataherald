from typing import Any

from pydantic import BaseModel, Field


class Organization(BaseModel):
    id: Any = Field(alias="_id")
    name: str
    db_alias: str | None
    slack_workspace_id: str | None
