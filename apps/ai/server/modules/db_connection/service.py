import httpx
from bson import ObjectId
from fastapi import UploadFile

from config import settings
from modules.db_connection.models.entities import DBConnection, DBConnectionRef
from modules.db_connection.models.requests import DBConnectionRequest
from modules.db_connection.models.responses import DBConnectionResponse
from modules.db_connection.repository import DBConnectionRepository
from modules.organization.service import OrganizationService
from utils.exception import raise_for_status
from utils.s3 import S3


class DBConnectionService:
    def __init__(self):
        self.repo = DBConnectionRepository()
        self.org_service = OrganizationService()

    def get_db_connections(self, org_id: str) -> list[DBConnectionResponse]:
        db_connection_refs = self.repo.get_db_connection_refs(org_id)
        db_connection_ids = [
            str(db_connection_ref.db_connection_id)
            for db_connection_ref in db_connection_refs
        ]
        db_connections = self.repo.get_db_connections(db_connection_ids)
        return [
            self._get_mapped_db_connection_response(db_connection)
            for db_connection in db_connections
        ]

    def get_db_connection(self, db_connection_id: str) -> DBConnectionResponse:
        db_connection = self.repo.get_db_connection(db_connection_id)
        return (
            self._get_mapped_db_connection_response(db_connection)
            if db_connection
            else None
        )

    async def add_db_connection(
        self,
        db_connection_request_json: dict,
        org_id: str,
        file: UploadFile = None,
    ) -> DBConnectionResponse:
        db_connection_request = DBConnectionRequest(**db_connection_request_json)

        if file:
            s3 = S3()
            db_connection_request.path_to_credentials_file = s3.upload(file)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/database-connections",
                json=db_connection_request.dict(),
            )

            raise_for_status(response.status_code, response.text)

            response_json = response.json()
            db_connection = DBConnection(**response_json)
            db_connection.id = ObjectId(response_json["id"])
            self.repo.add_db_connection_ref(
                DBConnectionRef(
                    alias=db_connection_request.alias,
                    db_connection_id=db_connection.id,
                    organization_id=ObjectId(org_id),
                ).dict(exclude={"id"})
            )

            self.org_service.update_db_connection_id(org_id, response_json["id"])

            return self._get_mapped_db_connection_response(db_connection)

    def _get_mapped_db_connection_response(
        self, db_connection: DBConnection
    ) -> DBConnectionResponse:
        db_connection_response = DBConnectionResponse(
            id=str(db_connection.id), **db_connection.dict(exclude={"id"})
        )
        db_connection_response.id = str(db_connection_response.id)
        return db_connection_response
