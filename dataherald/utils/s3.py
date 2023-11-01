import os

import boto3
from cryptography.fernet import InvalidToken

from dataherald.config import Settings
from dataherald.sql_database.models.types import FileStorage
from dataherald.utils.encrypt import FernetEncrypt


class S3:
    def __init__(self):
        self.settings = Settings()

    def upload(self, file_location, file_storage: FileStorage | None = None) -> str:
        file_name = file_location.split("/")[-1]
        bucket_name = "k2-core"

        # Upload the file
        if file_storage:
            fernet_encrypt = FernetEncrypt()
            bucket_name = file_storage.bucket
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=fernet_encrypt.decrypt(file_storage.access_key_id),
                aws_secret_access_key=fernet_encrypt.decrypt(
                    file_storage.secret_access_key
                ),
                region_name=file_storage.region,
            )
        else:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.settings.s3_aws_access_key_id,
                aws_secret_access_key=self.settings.s3_aws_secret_access_key,
            )
        s3_client.upload_file(
            file_location, bucket_name, os.path.basename(file_location)
        )
        os.remove(file_location)

        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": file_name},
            ExpiresIn=3600,  # The URL will expire in 3600 seconds (1 hour)
        )

    def download_url(self, path: str, file_storage: FileStorage | None = None) -> str:
        path = path.split("/")

        if file_storage:
            fernet_encrypt = FernetEncrypt()
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=fernet_encrypt.decrypt(file_storage.access_key_id),
                aws_secret_access_key=fernet_encrypt.decrypt(
                    file_storage.secret_access_key
                ),
                region_name=file_storage.region,
            )
        else:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.settings.s3_aws_access_key_id,
                aws_secret_access_key=self.settings.s3_aws_secret_access_key,
            )

        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": path[2], "Key": path[-1]},
            ExpiresIn=3600,  # The URL will expire in 3600 seconds (1 hour)
        )

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
