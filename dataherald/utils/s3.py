import os

import boto3
from cryptography.fernet import InvalidToken

from dataherald.config import Settings
from dataherald.utils.encrypt import FernetEncrypt


class S3:
    def __init__(self):
        self.settings = Settings()

    def upload(self, file_location) -> str:
        file_name = file_location.split("/")[-1]
        bucket_name = "k2-core"

        # Upload the file
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.settings.s3_aws_access_key_id,
            aws_secret_access_key=self.settings.s3_aws_secret_access_key,
        )
        s3_client.upload_file(
            file_location, bucket_name, os.path.basename(file_location)
        )
        os.remove(file_location)
        return f"s3://{bucket_name}/{file_name}"

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
