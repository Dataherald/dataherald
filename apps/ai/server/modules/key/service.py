import hashlib
import secrets

from config import settings
from modules.key.models.entities import APIKey
from modules.key.models.exceptions import (
    CannotCreateKeyError,
    CannotRevokeKeyError,
    KeyNameExistsError,
)
from modules.key.models.requests import KeyGenerationRequest
from modules.key.models.responses import KeyPreviewResponse, KeyResponse
from modules.key.repository import KeyRepository

KEY_PREFIX = "dh-"


class KeyService:
    def __init__(self):
        self.repo = KeyRepository()

    def get_keys(self, org_id: str) -> list[KeyPreviewResponse]:
        keys = self.repo.get_keys(org_id)
        return [KeyPreviewResponse(**key.dict(exclude_unset=True)) for key in keys]

    def add_key(
        self, key_request: KeyGenerationRequest, org_id: str, api_key: str = None
    ) -> KeyResponse:
        key = self.repo.get_key_by_name(key_request.name, org_id)
        if key:
            raise KeyNameExistsError(key.id, org_id)
        if not api_key:
            api_key = KEY_PREFIX + self.generate_new_key()
        key = APIKey(
            key_hash=self.hash_key(key=api_key),
            organization_id=org_id,
            name=key_request.name,
            key_preview=KEY_PREFIX + "························" + api_key[-3:],
        )
        key_id = self.repo.add_key(key)

        if key_id:
            new_key = self.repo.get_key(key_id, org_id)
            return KeyResponse(
                id=key_id,
                name=new_key.name,
                organization_id=new_key.organization_id,
                created_at=new_key.created_at,
                key_preview=new_key.key_preview,
                api_key=api_key,
            )

        raise CannotCreateKeyError(org_id)

    def validate_key(self, api_key: str) -> APIKey:
        return self.repo.get_key_by_hash(key_hash=self.hash_key(api_key))

    def hash_key(self, key: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256",  # The hash digest algorithm for HMAC
            key.encode("utf-8"),  # Convert the password to bytes
            settings.api_key_salt.encode("utf-8"),  # Provide the salt
            100000,  # It is recommended to use at least 100,000 iterations of SHA-256
        )

    def generate_new_key(self) -> str:
        while True:
            new_key = secrets.token_hex(32)
            if not self.repo.get_key_by_hash(key_hash=new_key):
                return new_key

    def revoke_key(self, key_id: str, org_id: str):
        if self.repo.delete_key(key_id, org_id) == 1:
            return {"id": key_id}

        raise CannotRevokeKeyError(key_id, org_id)
