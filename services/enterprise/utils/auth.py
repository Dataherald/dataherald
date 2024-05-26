import jwt
from bson import ObjectId
from fastapi import Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from config import (
    USER_COL,
    auth_settings,
)
from database.mongo import MongoDB
from exceptions.exceptions import UnknownError
from modules.auth.models.exceptions import (
    BearerTokenExpiredError,
    DecodeError,
    InvalidBearerTokenError,
    InvalidOrRevokedAPIKeyError,
    PyJWKClientError,
    UnauthorizedDataAccessError,
    UnauthorizedOperationError,
    UnauthorizedUserError,
)
from modules.key.service import KeyService
from modules.organization.service import OrganizationService
from modules.user.models.entities import Roles, User
from modules.user.models.exceptions import UserNotFoundError
from modules.user.service import UserService

user_service = UserService()
org_service = OrganizationService()
key_service = KeyService()


class User(User):
    pass


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
            raise PyJWKClientError() from error
        except jwt.exceptions.DecodeError as error:
            raise DecodeError() from error

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
            raise BearerTokenExpiredError() from error
        except (jwt.InvalidAudienceError, jwt.InvalidIssuerError) as error:
            raise InvalidBearerTokenError() from error
        except (jwt.DecodeError, jwt.InvalidTokenError) as error:
            raise InvalidBearerTokenError() from error
        except Exception as error:
            raise UnknownError(str(error)) from error


class Authorize:
    def user(self, payload: dict) -> User:
        sub = payload["sub"]
        user = user_service.get_user_by_sub(sub)
        if not user:
            raise UnauthorizedUserError(email=sub)
        return user

    def user_in_organization(self, user_id: str, org_id: str):
        if not MongoDB.find_one(
            USER_COL,
            {"_id": ObjectId(user_id), "organization_id": org_id},
        ):
            raise UserNotFoundError(user_id, org_id)

    def is_admin_user(self, user: User):
        if user.role != Roles.admin:
            raise UnauthorizedOperationError(user_id=user.id)

    def is_self(self, user_a_id: str, user_b_id: str):
        # TODO - fix param names to clear up confusion
        if user_a_id != user_b_id:
            raise UnauthorizedDataAccessError(user_id=user_a_id)

    def is_not_self(self, user_a_id: str, user_b_id: str):
        # TODO - fix param names to clear up confusion
        if user_a_id == user_b_id:
            raise UnauthorizedOperationError(user_id=user_a_id)


class MockHTTPBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(
            description="Mock HTTP Bearer authentication, use email as token",
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


api_key_header = APIKeyHeader(name="X-API-Key")
token_auth_scheme = HTTPBearer()
mock_auth_scheme = MockHTTPBearer()


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    validated_key = key_service.validate_key(api_key)
    if validated_key:
        return validated_key

    raise InvalidOrRevokedAPIKeyError(key_id=api_key)


def verify_token(token: dict = Security(token_auth_scheme)):
    VerifyToken(token.credentials).verify()
    return token


def get_auth_scheme():
    if auth_settings.auth_disabled:
        print("Auth is disabled")
        return mock_auth_scheme
    return token_auth_scheme


def authenticate_user(token=Security(get_auth_scheme())):
    payload = (
        {auth_settings.auth0_issuer + "email": token.credentials}
        if auth_settings.auth_disabled
        else VerifyToken(token.credentials).verify()
    )
    return Authorize().user(payload)
