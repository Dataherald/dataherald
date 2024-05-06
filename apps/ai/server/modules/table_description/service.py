import httpx

from config import settings
from exceptions.exception_handlers import raise_engine_exception
from modules.db_connection.service import DBConnectionService
from modules.table_description.models.entities import (
    DHTableDescriptionMetadata,
    TableDescription,
    TableDescriptionMetadata,
)
from modules.table_description.models.exceptions import TableDescriptionNotFoundError
from modules.table_description.models.requests import (
    ScanRequest,
    TableDescriptionRequest,
)
from modules.table_description.models.responses import (
    AggrTableDescription,
    BasicTableDescriptionResponse,
    DatabaseDescriptionResponse,
)
from modules.table_description.repository import TableDescriptionRepository
from utils.misc import reserved_key_in_metadata


class TableDescriptionService:
    def __init__(self):
        self.repo = TableDescriptionRepository()
        self.db_connection_service = DBConnectionService()

    async def get_table_descriptions(
        self, db_connection_id: str, table_name: str, org_id: str
    ) -> list[AggrTableDescription]:
        db_connection = self.db_connection_service.get_db_connection_in_org(
            db_connection_id, org_id
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + "/table-descriptions",
                params={"db_connection_id": db_connection_id, "table_name": table_name},
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            table_descriptions = [
                AggrTableDescription(
                    **table_description, db_connection_alias=db_connection.alias
                )
                for table_description in response.json()
            ]
            for table_description in table_descriptions:
                for column in table_description.columns:
                    column.categories = (
                        sorted(column.categories) if column.categories else None
                    )

            return table_descriptions

    async def get_table_description(
        self, table_description_id: str, org_id: str
    ) -> AggrTableDescription:
        table_description = self.get_table_description_in_org(
            table_description_id, org_id
        )
        db_connection = self.db_connection_service.get_db_connection_in_org(
            table_description.db_connection_id, org_id
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + f"/table-descriptions/{table_description_id}",
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            table_description = AggrTableDescription(
                **response.json(), db_connection_alias=db_connection.alias
            )
            for column in table_description.columns:
                column.categories = (
                    sorted(column.categories) if column.categories else None
                )

            return table_description

    async def refresh_table_description(
        self, org_id: str
    ) -> list[DatabaseDescriptionResponse]:
        database_description_list = []
        db_connections = self.db_connection_service.get_db_connections(org_id)

        for db_connection in db_connections:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.engine_url + "/table-descriptions/refresh",
                    json={"db_connection_id": db_connection.id},
                    timeout=settings.default_engine_timeout,
                )

                try:
                    raise_engine_exception(response, org_id=org_id)
                    table_descriptions = [
                        AggrTableDescription(**table_description)
                        for table_description in response.json()
                    ]

                    tables = [
                        BasicTableDescriptionResponse(
                            id=td.id,
                            name=td.table_name,
                            schema_name=td.schema_name,
                            columns=[c.name for c in td.columns],
                            sync_status=td.status,
                            last_sync=(
                                str(td.last_schema_sync)
                                if td.last_schema_sync
                                else None
                            ),
                        )
                        for td in table_descriptions
                    ]
                except Exception:
                    tables = []

                database_description_list.append(
                    DatabaseDescriptionResponse(
                        db_connection_id=db_connection.id,
                        db_connection_alias=db_connection.alias,
                        dialect=db_connection.dialect,
                        schemas=db_connection.schemas,
                        tables=tables,
                    )
                )

        return database_description_list

    async def get_database_description_list(
        self, org_id: str
    ) -> list[DatabaseDescriptionResponse]:
        database_description_list = []
        db_connections = self.db_connection_service.get_db_connections(org_id)
        for db_connection in db_connections:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    settings.engine_url + "/table-descriptions",
                    params={"db_connection_id": db_connection.id},
                    timeout=settings.default_engine_timeout,
                )
                raise_engine_exception(response, org_id=org_id)
                table_descriptions = [
                    AggrTableDescription(**table_description)
                    for table_description in response.json()
                ]

                tables = [
                    BasicTableDescriptionResponse(
                        id=td.id,
                        name=td.table_name,
                        columns=[c.name for c in td.columns],
                        schema_name=td.schema_name,
                        sync_status=td.status,
                        last_sync=(
                            str(td.last_schema_sync) if td.last_schema_sync else None
                        ),
                    )
                    for td in table_descriptions
                ]
                database_description_list.append(
                    DatabaseDescriptionResponse(
                        db_connection_id=db_connection.id,
                        db_connection_alias=db_connection.alias,
                        dialect=db_connection.dialect,
                        schemas=db_connection.schemas,
                        tables=tables,
                    )
                )
        return database_description_list

    async def sync_databases_schemas(
        self, scan_request: ScanRequest, org_id: str
    ) -> list[AggrTableDescription]:
        reserved_key_in_metadata(scan_request.metadata)
        db_connection_group = (
            self.repo.get_table_description_grouped_by_db_connection_id(
                scan_request.ids
            )
        )
        for db_dic in db_connection_group:
            self.db_connection_service.get_db_connection_in_org(
                str(db_dic["_id"]), org_id
            )
        scan_request.metadata = TableDescriptionMetadata(
            **scan_request.metadata,
            dh_internal=DHTableDescriptionMetadata(organization_id=org_id),
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/table-descriptions/sync-schemas",
                json=scan_request.dict(exclude_unset=True),
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            return [
                AggrTableDescription(**table_description)
                for table_description in response.json()
            ]

    async def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
        org_id: str,
    ) -> AggrTableDescription:
        reserved_key_in_metadata(table_description_request.metadata)
        table_description = self.get_table_description_in_org(
            table_description_id, org_id
        )
        db_connection = self.db_connection_service.get_db_connection_in_org(
            table_description.db_connection_id, org_id
        )
        table_description_request.metadata = TableDescriptionMetadata(
            **table_description_request.metadata,
            dh_internal=DHTableDescriptionMetadata(organization_id=org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.put(
                settings.engine_url + f"/table-descriptions/{table_description_id}",
                json=table_description_request.dict(exclude_unset=True),
            )
            raise_engine_exception(response, org_id=org_id)
            return AggrTableDescription(
                **response.json(), db_connection_alias=db_connection.alias
            )

    def get_table_description_in_org(
        self, table_description_id: str, org_id: str
    ) -> TableDescription:
        table_description = self.repo.get_table_description(
            table_description_id, org_id
        )
        if not table_description:
            raise TableDescriptionNotFoundError(table_description_id, org_id)
        return table_description
