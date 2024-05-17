import json

import httpx
from fastapi import UploadFile

from config import settings, ssh_settings
from exceptions.exception_handlers import raise_engine_exception
from modules.db_connection.models.entities import (
    DBConnection,
    DBConnectionMetadata,
    DHDBConnectionMetadata,
)
from modules.db_connection.models.exceptions import (
    DBConnectionAliasExistsError,
    DBConnectionNotFoundError,
)
from modules.db_connection.models.requests import DBConnectionRequest, SampleDBRequest
from modules.db_connection.models.responses import (
    DBConnectionResponse,
    SampleDBConnectionResponse,
)
from modules.db_connection.repository import DBConnectionRepository
from modules.organization.service import OrganizationService
from utils.analytics import Analytics, EventName, EventType
from utils.encrypt import FernetEncrypt
from utils.misc import reserved_key_in_metadata
from utils.s3 import S3
from utils.sample_db import SampleDB


class DBConnectionService:
    def __init__(self):
        self.repo = DBConnectionRepository()
        self.analytics = Analytics()
        self.sample_db = SampleDB()
        self.org_service = OrganizationService()

    def get_db_connections(self, org_id: str) -> list[DBConnectionResponse]:
        return sorted(self.repo.get_db_connections(org_id), key=lambda x: x.alias)

    def get_db_connection(
        self, db_connection_id: str, org_id: str
    ) -> DBConnectionResponse:
        return self.get_db_connection_in_org(db_connection_id, org_id)

    def upload_file(
        self, db_connection_request: DBConnectionRequest, file: UploadFile | None
    ) -> str | None:
        s3 = S3()
        if db_connection_request.bigquery_credential_file_content:
            return s3.create_and_upload(
                json.dumps(db_connection_request.bigquery_credential_file_content)
            )
        if file:
            return s3.upload(file)
        if db_connection_request.sqlite_file_path:
            return db_connection_request.sqlite_file_path
        return None

    async def add_db_connection(
        self,
        db_connection_request: DBConnectionRequest,
        org_id: str,
        file: UploadFile | None = None,
    ) -> DBConnectionResponse:
        reserved_key_in_metadata(db_connection_request.metadata)
        organization = self.org_service.get_organization(org_id)
        db_connection = self.repo.get_db_connection_by_alias(
            db_connection_request.alias, org_id
        )
        if db_connection:
            raise DBConnectionAliasExistsError(db_connection.id, org_id)

        db_connection_internal_request = DBConnection(
            **db_connection_request.dict(exclude_unset=True)
        )
        db_connection_internal_request.metadata = DBConnectionMetadata(
            **db_connection_request.metadata,
            dh_internal=DHDBConnectionMetadata(organization_id=org_id),
        )

        db_connection_internal_request.path_to_credentials_file = self.upload_file(
            db_connection_request, file
        )

        if organization.llm_api_key:
            db_connection_internal_request.llm_api_key = FernetEncrypt().decrypt(
                organization.llm_api_key
            )

        if db_connection_request.use_ssh:
            db_connection_internal_request.ssh_settings.private_key_password = (
                ssh_settings.private_key_password
            )
            db_connection_internal_request.path_to_credentials_file = (
                ssh_settings.path_to_credentials_file
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/database-connections",
                json=db_connection_internal_request.dict(),
                timeout=settings.default_engine_timeout,
            )

            raise_engine_exception(response, org_id=org_id)
            db_connection = DBConnectionResponse(**response.json())
            self.analytics.track(
                org_id,
                EventName.db_connection_created,
                EventType.db_connection_event(
                    id=db_connection.id,
                    organization_id=org_id,
                    database_type=self.get_database_type(
                        db_connection_request.connection_uri
                    ),
                ),
            )

            return db_connection

    async def update_db_connection(
        self,
        db_connection_id,
        db_connection_request: DBConnectionRequest,
        org_id: str,
        file: UploadFile | None = None,
    ) -> DBConnectionResponse:
        reserved_key_in_metadata(db_connection_request.metadata)
        organization = self.org_service.get_organization(org_id)
        db_connection_internal_request = DBConnection(
            **db_connection_request.dict(exclude_unset=True)
        )
        self.get_db_connection_in_org(db_connection_id, org_id)

        db_connection_internal_request.metadata = DBConnectionMetadata(
            **db_connection_request.metadata,
            dh_internal=DHDBConnectionMetadata(organization_id=org_id),
        )
        db_connection_internal_request.path_to_credentials_file = self.upload_file(
            db_connection_request, file
        )

        if organization.llm_api_key:
            db_connection_internal_request.llm_api_key = FernetEncrypt().decrypt(
                organization.llm_api_key
            )

        if db_connection_request.use_ssh:
            db_connection_internal_request.ssh_settings.private_key_password = (
                ssh_settings.private_key_password
            )
            db_connection_internal_request.path_to_credentials_file = (
                ssh_settings.path_to_credentials_file
            )

        async with httpx.AsyncClient() as client:
            response = await client.put(
                settings.engine_url + f"/database-connections/{db_connection_id}",
                json=db_connection_internal_request.dict(),
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            return DBConnectionResponse(**response.json())

    async def add_sample_db_connection(
        self, sample_request: SampleDBRequest, org_id: str
    ) -> DBConnectionResponse:
        sample_db_dict = await self.sample_db.add_sample_db(
            sample_request.sample_db_id, org_id
        )

        return self.get_db_connection_in_org(sample_db_dict.db_connection_id, org_id)

    def get_sample_db_connections(self) -> list[SampleDBConnectionResponse]:
        sample_dbs = self.sample_db.get_sample_dbs()
        return [
            SampleDBConnectionResponse(
                dialect=sdb.database_connection["dialect"],
                alias=sdb.name,
                **sdb.dict(exclude_unset=True),
            )
            for sdb in sample_dbs
        ]

    def get_db_connection_in_org(
        self, db_connection_id: str, org_id: str
    ) -> DBConnection:
        db_connection = self.repo.get_db_connection(db_connection_id, org_id)
        if not db_connection:
            raise DBConnectionNotFoundError(db_connection_id, org_id)
        return db_connection

    def get_database_type(self, connection_uri: str) -> str:
        return connection_uri.split(":")[0]
