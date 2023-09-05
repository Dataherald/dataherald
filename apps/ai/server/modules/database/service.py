import httpx
from fastapi import HTTPException, UploadFile, status

from config import settings
from modules.database.models.requests import (
    DatabaseConnectionRequest,
    ScanRequest,
    TableDescriptionRequest,
)
from modules.database.models.responses import ScannedDBResponse
from modules.organization.models.entities import Organization
from modules.organization.service import OrganizationService
from utils.s3 import S3


class DatabaseService:
    def __init__(self):
        self.org_service = OrganizationService()

    async def get_scanned_databases(
        self, organization_id: str
    ) -> list[ScannedDBResponse]:
        organization = self.org_service.get_organization(organization_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.k2_core_url
                + f"/scanned-databases?db_alias={organization.db_alias}"
            )
            response.raise_for_status()
            return [ScannedDBResponse(**response.json())]

    async def add_scanned_databases_description(
        self,
        db_alias: str,
        table_description_request: TableDescriptionRequest,
    ) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                settings.k2_core_url
                + f"/scanned-db/{db_alias}/{table_description_request.table_name}",
                json=table_description_request.dict(exclude={"table_name"}),
            )
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=response.json()
                )
            return True

    async def scan_database(self, scan_request: ScanRequest) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/scanner",
                json=scan_request.dict(),
            )
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=response.json()
                )
            return response.json()

    async def add_database_connection(
        self,
        database_connection_request: DatabaseConnectionRequest,
        organizaiton: Organization,
        file: UploadFile = None,
    ) -> bool:
        if file:
            s3 = S3()
            database_connection_request.path_to_credentials_file = s3.upload(file)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/database",
                json=database_connection_request.dict(),
            )

            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=response.json()
                )

            self.org_service.update_organization(
                str(organizaiton.id), {"db_alias": database_connection_request.db_alias}
            )

            return True
