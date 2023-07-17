from cryptography.fernet import Fernet

from dataherald.config import System


class FernetEncrypt:
    def __init__(self, system: System):
        self.fernet_key = Fernet(system.settings.require("encrypt_key"))

    def encrypt(self, input: str) -> str:
        return self.fernet_key.encrypt(input.encode()).decode("utf-8")

    def decrypt(self, input: str) -> str:
        return self.fernet_key.decrypt(input).decode("utf-8")
