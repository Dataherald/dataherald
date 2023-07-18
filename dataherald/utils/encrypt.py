from cryptography.fernet import Fernet

from dataherald.config import Settings


class FernetEncrypt:
    def __init__(self):
        settings = Settings()
        self.fernet_key = Fernet(settings.require("encrypt_key"))

    def encrypt(self, input: str) -> str:
        if not input:
            return ""
        return self.fernet_key.encrypt(input.encode()).decode("utf-8")

    def decrypt(self, input: str) -> str:
        if input == "":
            return ""
        return self.fernet_key.decrypt(input).decode("utf-8")
