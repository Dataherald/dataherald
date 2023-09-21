from bson import ObjectId
from fastapi import HTTPException, status

from modules.organization.models.entities import Organization, SlackInstallation
from modules.organization.models.requests import OrganizationRequest
from modules.organization.models.responses import OrganizationResponse
from modules.organization.repository import OrganizationRepository


class OrganizationService:
    def __init__(self):
        self.repo = OrganizationRepository()

    def get_organizations(self) -> list[OrganizationResponse]:
        organizations = self.repo.get_organizations()
        return [self._get_mapped_organization_response(org) for org in organizations]

    def get_organization(self, org_id: str) -> OrganizationResponse:
        organization = self.repo.get_organization(org_id)
        if organization:
            return self._get_mapped_organization_response(organization)
        return None

    def get_organization_by_slack_workspace_id(
        self, workspace_id: str
    ) -> OrganizationResponse:
        organization = self.repo.get_organization_by_slack_workspace_id(workspace_id)
        if organization:
            return self._get_mapped_organization_response(organization)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    def add_organization(
        self, org_request: OrganizationRequest
    ) -> OrganizationResponse:
        new_org_data = Organization(**org_request.dict())
        new_org_data.db_connection_id = ObjectId(new_org_data.db_connection_id)
        new_id = self.repo.add_organization(new_org_data.dict(exclude={"id"}))
        if new_id:
            new_org = self.repo.get_organization(new_id)
            return self._get_mapped_organization_response(new_org)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization exists or cannot add organization",
        )

    def update_organization(
        self, org_id: str, org_request: OrganizationRequest
    ) -> OrganizationResponse:
        if self.repo.update_organization(org_id, org_request.dict()) == 1:
            new_org = self.repo.get_organization(org_id)
            return self._get_mapped_organization_response(new_org)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found or cannot be updated",
        )

    def delete_organization(self, org_id: str) -> dict:
        if self.repo.delete_organization(org_id) == 1:
            return {"id": org_id}

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found or cannot be deleted",
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
            new_org = self.repo.get_organization(new_id)
            return self._get_mapped_organization_response(new_org)

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

    def update_db_connection_id(
        self, org_id: str, db_connection_id: str
    ) -> OrganizationResponse:
        if self.repo.update_db_connection_id(org_id, db_connection_id) == 1:
            new_org = self.repo.get_organization(org_id)
            return self._get_mapped_organization_response(new_org)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found or cannot be updated",
        )

    def _get_mapped_organization_response(
        self, organization: Organization
    ) -> OrganizationResponse:
        org_dict = organization.dict()
        org_dict["id"] = str(org_dict["id"])
        org_dict["db_connection_id"] = (
            str(org_dict["db_connection_id"]) if org_dict["db_connection_id"] else None
        )
        return OrganizationResponse(**org_dict)
