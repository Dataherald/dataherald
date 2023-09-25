import httpx

from config import settings
from modules.db_connection.service import DBConnectionService
from modules.table_description.models.requests import (
    ScanRequest,
    TableDescriptionRequest,
)
from modules.table_description.models.responses import (
    BasicTableDescriptionResponse,
    DatabaseDescriptionResponse,
    TableDescriptionResponse,
)
from utils.exception import raise_for_status


class TableDescriptionService:
    def __init__(self):
        self.db_connection_service = DBConnectionService()

    async def get_table_descriptions(
        self, table_name: str, db_connection_id: str
    ) -> list[TableDescriptionResponse]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.k2_core_url + "/table-descriptions",
                params={"db_connection_id": db_connection_id, "table_name": table_name},
            )
            raise_for_status(response.status_code, response.text)
            return [TableDescriptionResponse(**td) for td in response.json()]

    async def get_database_table_descriptions(self, db_connection_id: str):
        if not db_connection_id:
            return []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.k2_core_url + "/table-descriptions",
                params={"db_connection_id": db_connection_id, "table_name": ""},
            )
            raise_for_status(response.status_code, response.text)
            db_connection = self.db_connection_service.get_db_connection(
                db_connection_id
            )

            table_descriptions = [
                TableDescriptionResponse(**td) for td in response.json()
            ]
            tables = [
                BasicTableDescriptionResponse(
                    id=td.id,
                    name=td.table_name,
                    columns=[c.name for c in td.columns],
                    schemas_status=td.schemas_status,
                    last_schemas_sync=td.last_schemas_sync,
                )
                for td in table_descriptions
            ]
            return [
                DatabaseDescriptionResponse(alias=db_connection.alias, tables=tables)
            ]

    async def sync_table_descriptions_schemas(self, scan_request: ScanRequest) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/table-descriptions/sync-schemas",
                json=scan_request.dict(),
            )
            raise_for_status(response.status_code, response.text)
            return response.json()

    async def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
    ) -> TableDescriptionResponse:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                settings.k2_core_url + f"/table-descriptions/{table_description_id}",
                json=table_description_request.dict(exclude={"table_name"}),
            )
            raise_for_status(response.status_code, response.text)
            return TableDescriptionResponse(**response.json())

    async def delete_table_description(self, table_description_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.k2_core_url + f"/table-descriptions/{table_description_id}",
            )
            raise_for_status(response.status_code, response.text)
            return True
