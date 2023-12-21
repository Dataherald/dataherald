from datetime import datetime

import openai
from fastapi import HTTPException, status

from modules.organization.models.entities import Organization, SlackInstallation
from modules.organization.models.requests import OrganizationRequest
from modules.organization.models.responses import OrganizationResponse
from modules.organization.repository import OrganizationRepository
from utils.encrypt import FernetEncrypt


class OrganizationService:
    def __init__(self):
        self.repo = OrganizationRepository()

    def get_organizations(self) -> list[OrganizationResponse]:
        return self.repo.get_organizations()

    def get_organization(self, org_id: str) -> OrganizationResponse:
        return self.repo.get_organization(org_id)

    def get_organization_by_slack_workspace_id(
        self, workspace_id: str
    ) -> OrganizationResponse:
        organization = self.repo.get_organization_by_slack_workspace_id(workspace_id)
        if organization:
            return organization

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    def add_organization(
        self, org_request: OrganizationRequest
    ) -> OrganizationResponse:
        if org_request.llm_api_key:
            self._validate_api_key(org_request.llm_api_key)
            org_request.llm_api_key = self._encrypt_llm_credentials(
                org_request.llm_api_key
            )
        new_org_data = Organization(**org_request.dict(), created_at=datetime.now())
        new_org_data.db_connection_id = new_org_data.db_connection_id

        new_org_data.confidence_threshold = (
            1.0
            if new_org_data.confidence_threshold is None
            else new_org_data.confidence_threshold
        )

        new_id = self.repo.add_organization(new_org_data.dict(exclude_unset=True))
        if new_id:
            new_org = self.repo.get_organization(new_id)
            return OrganizationResponse(**new_org.dict())

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization exists or cannot add organization",
        )

    def update_organization(
        self, org_id: str, org_request: OrganizationRequest
    ) -> OrganizationResponse:
        if org_request.llm_api_key:
            self._validate_api_key(org_request.llm_api_key)
            org_request.llm_api_key = self._encrypt_llm_credentials(
                org_request.llm_api_key
            )
        updated_org_data = Organization(**org_request.dict(exclude_unset=True))
        updated_org_data.db_connection_id = updated_org_data.db_connection_id

        if (
            self.repo.update_organization(
                org_id, updated_org_data.dict(exclude_unset=True)
            )
            == 1
        ):
            new_org = self.repo.get_organization(org_id)

            if new_org.llm_api_key:
                self.repo.update_db_connections_llm_api_key(org_id, new_org.llm_api_key)

            return new_org

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
        current_org = self.repo.get_organization_by_slack_workspace_id(
            slack_installation_request.team.id
        )
        if current_org:  # update
            if (
                self.repo.update_organization(
                    str(current_org.id),
                    {"slack_installation": slack_installation_request.dict()},
                )
                == 1
            ):
                updated_org = self.repo.get_organization(str(current_org.id))
                return OrganizationResponse(**updated_org.dict())

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error ocurred while updating organization",
            )

        new_org_data = Organization(
            name=slack_installation_request.team.name,
            slack_installation=slack_installation_request,
            confidence_threshold=1.0,
            created_at=datetime.now(),
        )

        new_id = self.repo.add_organization(new_org_data.dict(exclude={"id"}))
        if new_id:
            return self.repo.get_organization(new_id)

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
        if (
            self.repo.update_organization(
                org_id, {"db_connection_id": db_connection_id}
            )
            == 1
        ):
            return self.repo.get_organization(org_id)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found or cannot be updated",
        )

    def _encrypt_llm_credentials(self, llm_api_key: str) -> str:
        fernet_encrypt = FernetEncrypt()
        return fernet_encrypt.encrypt(llm_api_key)

    def _validate_api_key(self, llm_api_key: str):
        openai.api_key = llm_api_key
        try:
            openai.Model.list()
        except openai.error.AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid LLM API key",
            ) from e
