import httpx
from fastapi import HTTPException, status

from config import settings
from modules.db_connection.service import DBConnectionService
from modules.organization.service import OrganizationService
from modules.table_description.models.requests import (
    ScanRequest,
    TableDescriptionRequest,
)
from modules.table_description.models.responses import (
    BasicTableDescriptionResponse,
    DatabaseDescriptionResponse,
    TableDescriptionResponse,
)
from modules.table_description.repository import TableDescriptionRepository
from utils.exception import raise_for_status
from utils.misc import reserved_key_in_metadata


class TableDescriptionService:
    def __init__(self):
        self.repo = TableDescriptionRepository()
        self.org_service = OrganizationService()
        self.db_connection_service = DBConnectionService()

    async def get_table_descriptions(
        self, db_connection_id: str, table_name: str, org_id: str
    ) -> list[TableDescriptionResponse]:
        if not self.db_connection_service.get_db_connection(db_connection_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database connection not found",
            )

        table_descriptions = self.repo.get_table_descriptions(
            db_connection_id, table_name
        )

        for table_description in table_descriptions:
            for column in table_description.columns:
                column.categories = (
                    sorted(column.categories) if column.categories else None
                )
        return table_descriptions

    async def get_table_description(
        self, table_description_id: str, org_id: str
    ) -> TableDescriptionResponse:
        if not self.table_description_in_organization(table_description_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table Description not found",
            )

        table_description = self.repo.get_table_description(table_description_id)

        for column in table_description.columns:
            column.categories = sorted(column.categories) if column.categories else None

        return table_description

    async def get_database_table_descriptions(self, org_id: str):
        organization = self.org_service.get_organization(org_id)
        db_connection = self.db_connection_service.get_db_connection(
            organization.db_connection_id, org_id
        )
        table_descriptions = self.repo.get_table_descriptions(db_connection.id)

        tables = [
            BasicTableDescriptionResponse(
                id=td.id,
                name=td.table_name,
                columns=[c.name for c in td.columns],
                sync_status=td.status,
                last_sync=str(td.last_schema_sync) if td.last_schema_sync else None,
            )
            for td in table_descriptions
        ]
        return [
            DatabaseDescriptionResponse(
                alias=db_connection.alias,
                tables=tables,
                db_connection_id=db_connection.id,
            )
        ]

    async def sync_table_descriptions_schemas(
        self, scan_request: ScanRequest, org_id: str
    ) -> bool:
        db_connection = self.db_connection_service.get_db_connection(
            scan_request.db_connection_id, org_id
        )

        if not db_connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database connection not found",
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/table-descriptions/sync-schemas",
                json=scan_request.dict(),
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            return response.json()

    async def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
        org_id: str,
    ) -> TableDescriptionResponse:
        reserved_key_in_metadata(table_description_request.metadata)
        if not self.table_description_in_organization(table_description_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table Description not found",
            )

        async with httpx.AsyncClient() as client:
            response = await client.put(
                settings.engine_url + f"/table-descriptions/{table_description_id}",
                json=table_description_request.dict(exclude_unset=True),
            )
            raise_for_status(response.status_code, response.text)
            return TableDescriptionResponse(**response.json())

    async def delete_table_description(self, table_description_id: str, org_id: str):
        if not self.table_description_in_organization(table_description_id, org_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table Description not found",
            )

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.engine_url + f"/table-descriptions/{table_description_id}",
            )
            raise_for_status(response.status_code, response.text)
            return True

    def table_description_in_organization(
        self, table_description_id: str, org_id: str
    ) -> bool:
        table_description = self.repo.get_table_description(table_description_id)

        db_connection = self.db_connection_service.get_db_connection(
            table_description.db_connection_id, org_id
        )

        return True if db_connection else False
