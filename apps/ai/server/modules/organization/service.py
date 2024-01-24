from datetime import datetime

import openai
from fastapi import HTTPException, status

from modules.organization.models.entities import (
    Organization,
    SlackConfig,
    SlackInstallation,
)
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
        organization = Organization(**org_request.dict(), created_at=datetime.now())
        organization.slack_config.db_connection_id = (
            organization.slack_config.db_connection_id
        )

        organization.confidence_threshold = (
            1.0
            if organization.confidence_threshold is None
            else organization.confidence_threshold
        )

        new_id = self.repo.add_organization(organization.dict(exclude_unset=True))
        if new_id:
            new_organization = self.repo.get_organization(new_id)
            return OrganizationResponse(**new_organization.dict())

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
        organization = Organization(**org_request.dict(exclude_unset=True))
        organization.slack_config.db_connection_id = (
            organization.slack_config.db_connection_id
        )

        if (
            self.repo.update_organization(org_id, organization.dict(exclude_unset=True))
            == 1
        ):
            return self.repo.get_organization(org_id)

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
    ) -> OrganizationResponse:
        current_org = self.repo.get_organization_by_slack_workspace_id(
            slack_installation_request.team.id
        )
        if current_org:  # update
            if (
                self.repo.update_organization(
                    str(current_org.id),
                    {
                        "slack_config.slack_installation": slack_installation_request.dict()
                    },
                )
                == 1
            ):
                updated_org = self.repo.get_organization(str(current_org.id))
                return OrganizationResponse(**updated_org.dict())

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error ocurred while updating organization",
            )

        organization = Organization(
            name=slack_installation_request.team.name,
            slack_config=SlackConfig(slack_installation_request, db_connection_id=None),
            confidence_threshold=1.0,
            created_at=datetime.now(),
        )

        new_id = self.repo.add_organization(organization.dict(exclude={"id"}))
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
            return organization.slack_config.slack_installation

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="slack installation not found"
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
