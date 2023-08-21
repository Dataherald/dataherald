from fastapi import HTTPException

from modules.organization.models.entities import Organization
from modules.organization.models.requests import OrganizationRequest
from modules.organization.repository import OrganizationRepository


class OrganizationService:
    def __init__(self):
        self.repo = OrganizationRepository()

    def list_organizations(self) -> list[Organization]:
        organizations = self.repo.list_organizations()
        for organization in organizations:
            organization.id = str(organization.id)
        return organizations

    def get_organization(self, id: str) -> Organization:
        organization = self.repo.get_organization(id)
        if organization:
            organization.id = str(organization.id)
            return organization
        return None

    def get_organization_with_slack_workspace_id(self, workspace_id) -> Organization:
        organization = self.repo.get_organization_with_slack_workspace_id(workspace_id)
        if organization:
            organization.id = str(organization.id)
            return organization
        return None

    def delete_organization(self, id: str):
        if self.repo.delete_organization(id) == 1:
            return {"id": id}

        raise HTTPException(
            status_code=400, detail="Organization not found or cannot be deleted"
        )

    def update_organization(self, id: str, org_request: dict) -> Organization:
        new_org_data = Organization(**org_request)
        if self.repo.update_organization(id, new_org_data.dict(exclude={"id"})) == 1:
            new_org = self.repo.get_organization(id)
            new_org.id = str(new_org.id)
            return new_org

        raise HTTPException(
            status_code=400, detail="Organization not found or cannot be updated"
        )

    def add_organization(self, org_request: OrganizationRequest) -> Organization:
        new_org_data = Organization(**org_request.dict())
        new_id = self.repo.add_organization(new_org_data.dict(exclude={"id"}))
        if new_id:
            new_org = self.repo.get_organization(new_id)
            new_org.id = str(new_org.id)
            return new_org

        raise HTTPException(
            status_code=400, detail="Organization exists or cannot add organization"
        )
