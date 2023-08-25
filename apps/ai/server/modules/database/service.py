import httpx
from fastapi import HTTPException, status

from config import settings
from modules.database.models.requests import TableDescriptionRequest
from modules.database.models.responses import ScannedDBResponse
from modules.organization.repository import OrganizationRepository


class DatabaseService:
    def __init__(self):
        self.organization_repo = OrganizationRepository()

    async def get_scanned_databases(
        self, organization_id: str
    ) -> list[ScannedDBResponse]:
        organization = self.organization_repo.get_organization(organization_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.k2_core_url
                + f"/scanned-databases?db_alias={organization.db_alias}"
            )
            response.raise_for_status()
            return [ScannedDBResponse(**response.json())]

    async def add_scanned_databases_description(
        self,
        db_name: str,
        table_name: str,
        table_description_request: TableDescriptionRequest,
    ) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                settings.k2_core_url + f"/scanned-db/{db_name}/{table_name}",
                json=table_description_request.dict(),
            )
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=response.json()
                )
            return True
