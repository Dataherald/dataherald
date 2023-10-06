import re

import jwt
from bson import ObjectId
from fastapi import HTTPException, status

from config import (
    DATABASE_CONNECTION_REF_COL,
    GOLDEN_SQL_REF_COL,
    INSTRUCTION_COL,
    QUERY_RESPONSE_REF_COL,
    TABLE_DESCRIPTION_COL,
    USER_COL,
    auth_settings,
)
from database.mongo import MongoDB
from modules.organization.models.responses import OrganizationResponse
from modules.organization.service import OrganizationService
from modules.query.service import QueryService
from modules.user.models.responses import UserResponse
from modules.user.service import UserService

user_service = UserService()
org_service = OrganizationService()
query_service = QueryService()


class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{auth_settings.auth0_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        self._fetch_signing_key()
        return self._decode_payload()

    def _fetch_signing_key(self):
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
            ) from error
        except jwt.exceptions.DecodeError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
            ) from error

    def _decode_payload(self):
        try:
            return jwt.decode(
                self.token,
                self.signing_key,
                algorithms=auth_settings.auth0_algorithms,
                audience=auth_settings.auth0_audience,
                issuer=auth_settings.auth0_issuer,
            )
        except jwt.ExpiredSignatureError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            ) from error
        except (jwt.InvalidAudienceError, jwt.InvalidIssuerError) as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token is invalid"
            ) from error
        except (jwt.DecodeError, jwt.InvalidTokenError) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid"
            ) from error
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            ) from e


class Authorize:
    def user(self, payload: dict) -> UserResponse:
        email = payload[auth_settings.auth0_issuer + "email"]
        user = user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
            )
        return user

    def instruction_in_organization(
        self, instruction_id: str, organization: OrganizationResponse
    ):
        instruction = MongoDB.find_one(
            INSTRUCTION_COL,
            {
                "_id": ObjectId(instruction_id),
                "db_connection_id": organization.db_connection_id,
            },
        )

        if not instruction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Instruction not found"
            )

    def db_connection_in_organization(self, db_connection_id: str, org_id: str):
        self._item_in_organization(
            DATABASE_CONNECTION_REF_COL,
            db_connection_id,
            org_id,
            key="db_connection_id",
        )

    def query_in_organization(self, query_id: str, org_id: str):
        self._item_in_organization(QUERY_RESPONSE_REF_COL, query_id, org_id)

    def golden_sql_in_organization(self, golden_sql_id: str, org_id: str):
        self._item_in_organization(
            GOLDEN_SQL_REF_COL, golden_sql_id, org_id, key="golden_sql_id"
        )

    def user_in_organization(self, user_id: str, org_id: str):
        self._item_in_organization(USER_COL, user_id, org_id)

    def table_description_in_organization(self, table_description_id: str, org_id: str):
        organization = org_service.get_organization(org_id)
        table_description = MongoDB.find_one(
            TABLE_DESCRIPTION_COL,
            {
                "_id": ObjectId(table_description_id),
                "db_connection_id": organization.db_connection_id,
            },
        )
        if not table_description:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )

    def get_organization_by_user_response(
        self, user: UserResponse
    ) -> OrganizationResponse:
        organization = org_service.get_organization(user.organization_id)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not belong to an Organization",
            )
        return organization

    def is_root_user(self, payload: dict):
        domain_pattern = r"@([A-Za-z0-9.-]+)"
        user = self.user(payload)
        match = re.search(domain_pattern, user.email)
        if match:
            domain = match.group(1)
            if domain == "dataherald.com":
                return

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
        )

    def _item_in_organization(
        self, collection: str, id: str, org_id: str, key: str = None
    ):
        if key:
            item = MongoDB.find_one(
                collection, {key: ObjectId(id), "organization_id": ObjectId(org_id)}
            )
        else:
            item = MongoDB.find_one(
                collection, {"_id": ObjectId(id), "organization_id": ObjectId(org_id)}
            )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
