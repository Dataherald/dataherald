import jwt
from bson import ObjectId
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config import (
    USER_COL,
    auth_settings,
)
from database.mongo import MongoDB
from modules.key.service import KeyService
from modules.organization.service import OrganizationService
from modules.user.models.entities import Roles
from modules.user.models.responses import UserResponse
from modules.user.service import UserService

user_service = UserService()
org_service = OrganizationService()
key_service = KeyService()


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

    def user_in_organization(self, user_id: str, org_id: str):
        self._item_in_organization(USER_COL, user_id, org_id)

    def is_admin_user(self, user: UserResponse):
        if user.role != Roles.admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
            )

    def is_self(self, id_a: str, id_b: str):
        if id_a != id_b:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authorized to access other user data",
            )

    def is_not_self(self, id_a: str, id_b: str):
        if id_a == id_b:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authorized to self modify  user data",
            )

    def _item_in_organization(
        self,
        collection: str,
        id: str,
        org_id: str,
        key: str = "_id",
        is_metadata: bool = False,
    ):
        metadata_prefix = "metadata" if is_metadata else ""
        item = MongoDB.find_one(
            collection,
            {key: ObjectId(id), f"{metadata_prefix}organization_id": org_id},
        )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )


api_key_header = APIKeyHeader(name="X-API-Key")


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    validated_key = key_service.validate_key(api_key)
    if validated_key:
        return validated_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key does not exist"
    )
