from bson import ObjectId
from fastapi import HTTPException, status

from modules.organization.models.entities import Organization, SlackInstallation
from modules.organization.models.requests import OrganizationRequest
from modules.organization.repository import OrganizationRepository


class OrganizationService:
    def __init__(self):
        self.repo = OrganizationRepository()

    def get_organizations(self) -> list[Organization]:
        organizations = self.repo.get_organizations()
        for organization in organizations:
            organization.id = str(organization.id)
        return organizations

    def get_organization(self, org_id: str) -> Organization:
        organization = self.repo.get_organization(ObjectId(org_id))
        if organization:
            organization.id = str(organization.id)
            return organization
        return None

    def get_organization_by_slack_workspace_id(self, workspace_id: str) -> Organization:
        organization = self.repo.get_organization_by_slack_workspace_id(workspace_id)
        if organization:
            organization.id = str(organization.id)
            return organization

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    def delete_organization(self, org_id: str):
        if self.repo.delete_organization(ObjectId(org_id)) == 1:
            return {"id": org_id}

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found or cannot be deleted",
        )

    def update_organization(self, org_id: str, org_request: dict) -> Organization:
        if "_id" in org_request:
            org_request.pop("_id")
        if self.repo.update_organization(ObjectId(org_id), org_request) == 1:
            new_org = self.repo.get_organization(ObjectId(org_id))
            new_org.id = str(new_org.id)
            return new_org

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found or cannot be updated",
        )

    def add_organization(self, org_request: OrganizationRequest) -> Organization:
        new_org_data = Organization(**org_request.dict())
        new_id = self.repo.add_organization(new_org_data.dict(exclude={"id"}))
        if new_id:
            new_org = self.repo.get_organization(ObjectId(new_id))
            new_org.id = str(new_org.id)
            return new_org

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization exists or cannot add organization",
        )

    def add_organization_by_slack_installation(
        self, slack_installation_request: SlackInstallation
    ):
        new_org_data = Organization(
            name=slack_installation_request.team.name,
            slack_installation=slack_installation_request,
        )

        new_id = self.repo.add_organization(new_org_data.dict(exclude={"id"}))
        if new_id:
            new_org = self.repo.get_organization(ObjectId(new_id))
            new_org.id = str(new_org.id)
            return new_org

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization exists or cannot add organization",
        )

    def get_slack_installation_by_slack_workspace_id(
        self, slack_workspace_id: str
    ) -> SlackInstallation:
        organization = self.repo.get_organization_by_slack_workspace_id(
            slack_workspace_id
        )
        if organization:
            return organization.slack_installation

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="slack installation not found"
        )
