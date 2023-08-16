from pydantic import BaseModel


class OrganizationRequest(BaseModel):
    name: str
    db_alias: str | None
    slack_workspace_id: str | None
