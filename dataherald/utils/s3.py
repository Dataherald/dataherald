import boto3
from cryptography.fernet import InvalidToken

from dataherald.config import Settings
from dataherald.utils.encrypt import FernetEncrypt


class S3:
    def __init__(self):
        self.settings = Settings()

    def download(self, path: str) -> str:
        fernet_encrypt = FernetEncrypt()
        path = path.split("/")
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.settings.s3_aws_access_key_id,
            aws_secret_access_key=self.settings.s3_aws_secret_access_key,
        )
        file_location = f"tmp/{path[-1]}"
        s3_client.download_file(
            Bucket=path[2], Key=f"{path[-1]}", Filename=file_location
        )
        # Decrypt file content if it is encrypted
        try:
            with open(file_location) as file_object:
                decrypted_content = fernet_encrypt.decrypt(file_object.read())
            with open(file_location, "w") as file_object:
                file_object.write(decrypted_content)
        except InvalidToken:
            pass

        return file_location
