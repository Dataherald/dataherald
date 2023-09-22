from modules.organization.models.entities import BaseOrganization


class OrganizationResponse(BaseOrganization):
    id: str
    db_connection_id: str
