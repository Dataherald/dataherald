from pydantic import Field

from modules.organization.models.entities import BaseOrganization


class OrganizationResponse(BaseOrganization):
    id: str = Field(alias="_id")
    db_connection_id: str
