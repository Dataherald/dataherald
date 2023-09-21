import re

import jwt
from bson import ObjectId
from fastapi import HTTPException, status

from config import (
    DATABASE_CONNECTION_REF_COL,
    GOLDEN_SQL_REF_COL,
    QUERY_RESPONSE_REF_COL,
    TABLE_DESCRIPTION_COL,
    USER_COL,
    auth_settings,
    slack_settings,
)
from database.mongo import MongoDB
from modules.organization.models.entities import (
    SlackBot,
    SlackInstallation,
    SlackTeam,
    SlackUser,
)
from modules.organization.models.responses import OrganizationResponse
from modules.organization.service import OrganizationService
from modules.query.service import QueryService
from modules.user.models.entities import User
from modules.user.service import UserService

user_service = UserService()
org_service = OrganizationService()
query_service = QueryService()

test_user = User(
    _id=ObjectId(b"lao-gan-maaa"),
    email="test@dataherald.com",
    email_verified=True,
    name="Test User",
    organization_id=ObjectId(b"foo-bar-quux"),
)

test_organization = OrganizationResponse(
    id="64ee518fadb29ccf33d51739",
    name="Test Org",
    db_connection_id="64ee518fadb29ccf33d51124",
    slack_installation=SlackInstallation(
        team=SlackTeam(id="TT1TV3MSL", name="test_org"),
        bot=SlackBot(
            scopes=[],
            token=slack_settings.slack_bot_access_token,
            user_id="test_bot_id",
            id="test_bot_id",
        ),
        user=SlackUser(
            token="test_user_token",  # noqa: S106
            scopes="test_scopes",
            id="test_user_id",
        ),
        enterprise="test_enterprise",
        token_type="test_token_type",  # noqa: S106
        is_enterprise_install=True,
        app_id="test_app_id",
        auth_version="test_auth_version",
    ),
    slack_workspace_id="test_slack_id",
    slack_bot_access_token=slack_settings.slack_bot_access_token,
    confidence_threshold=0.70,
)


class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{auth_settings.auth0_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # return mock authentication data
        if not auth_settings.auth_enabled:
            return {
                auth_settings.auth0_issuer + "email": test_user.email,  # placeholder
                "iss": auth_settings.auth0_issuer,
                "sub": "foo",
                "aud": auth_settings.auth0_audience,
                "iat": "",
                "exp": "",
                "azp": "",
                "scope": "openid profile email offline_access",
                "gty": "client-credentials",
            }
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error.__str__()
            ) from jwt.exceptions.PyJWKClientError
        except jwt.exceptions.DecodeError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error.__str__()
            ) from jwt.exceptions.DecodeError
        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=auth_settings.auth0_algorithms,
                audience=auth_settings.auth0_audience,
                issuer=auth_settings.auth0_issuer,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from Exception
        return payload


class Authorize:
    def user(self, payload: dict) -> User:
        if not auth_settings.auth_enabled:
            return test_user

        email = payload[auth_settings.auth0_issuer + "email"]
        user = user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
            )
        return user

    def db_connection_in_organization(self, db_connection_id: str, org_id: str):
        self._item_in_organization(
            DATABASE_CONNECTION_REF_COL,
            db_connection_id,
            org_id,
            key="db_connection_id",
        )

    def query_in_organization(self, query_id: str, org_id: str):
        self._item_in_organization(
            QUERY_RESPONSE_REF_COL, query_id, org_id, key="query_response_id"
        )

    def golden_sql_in_organization(self, golden_sql_id: str, org_id: str):
        self._item_in_organization(
            GOLDEN_SQL_REF_COL, golden_sql_id, org_id, key="golden_sql_id"
        )

    def user_in_organization(self, user_id: str, org_id: str):
        self._item_in_organization(USER_COL, user_id, org_id)

    def user_and_get_org_id(self, payload) -> str:
        user = self.user(payload)
        return str(self.get_organization_by_user(user).id)

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

    def get_organization_by_user(self, user: User) -> OrganizationResponse:
        if not auth_settings.auth_enabled:
            return test_organization

        organization = org_service.get_organization(str(user.organization_id))
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not belong to an Organization",
            )
        return organization

    def is_root_user(self, payload: dict):
        if not auth_settings.auth_enabled:
            return
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
        if not auth_settings.auth_enabled:
            return

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
