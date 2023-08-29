from typing import Any

from pydantic import Field

from modules.organization.models.requests import OrganizationRequest


class Organization(OrganizationRequest):
    id: Any = Field(alias="_id")
