import httpx

from config import settings
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
