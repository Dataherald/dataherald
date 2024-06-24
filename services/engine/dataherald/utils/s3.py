import os

import boto3
from cryptography.fernet import InvalidToken

from dataherald.config import Settings
from dataherald.sql_database.models.types import FileStorage
from dataherald.utils.encrypt import FernetEncrypt


class S3:
    def __init__(self):
        self.settings = Settings()

    def _get_client(
        self,
        access_key: str | None = None,
        secret_access_key: str | None = None,
        region: str | None = None,
    ) -> boto3.client:
        _access_key = access_key or self.settings.s3_aws_access_key_id
        _secret_access_key = secret_access_key or self.settings.s3_aws_secret_access_key
        _region = region or self.settings.s3_region

        if self.settings.s3_custom_endpoint:
            return boto3.client(
                "s3",
                endpoint_url=self.settings.s3_custom_endpoint,
                aws_session_token=None,
                aws_access_key_id=_access_key,
                aws_secret_access_key=_secret_access_key,
                region_name=_region,
            )

        return boto3.client(
            "s3",
            aws_access_key_id=_access_key,
            aws_secret_access_key=_secret_access_key,
            region_name=_region,
        )

    def upload(self, file_location, file_storage: FileStorage | None = None) -> str:
        file_name = file_location.split("/")[-1]
        bucket_name = self.settings.s3_bucket_name

        # Upload the file
        if file_storage:
            fernet_encrypt = FernetEncrypt()
            bucket_name = file_storage.bucket
            s3_client = self._get_client(
                access_key=fernet_encrypt.decrypt(file_storage.access_key_id),
                secret_access_key=fernet_encrypt.decrypt(
                    file_storage.secret_access_key
                ),
                region=file_storage.region,
            )
        else:
            s3_client = self._get_client()

        s3_client.upload_file(
            file_location, bucket_name, os.path.basename(file_location)
        )
        os.remove(file_location)
        return f"s3://{bucket_name}/{file_name}"

    def download(self, path: str, file_storage: FileStorage | None = None) -> str:
        fernet_encrypt = FernetEncrypt()
        path = path.split("/")
        if file_storage:
            fernet_encrypt = FernetEncrypt()
            s3_client = self._get_client(
                access_key=fernet_encrypt.decrypt(file_storage.access_key_id),
                secret_access_key=fernet_encrypt.decrypt(
                    file_storage.secret_access_key
                ),
                region=file_storage.region,
            )
        else:
            s3_client = self._get_client()

        file_location = f"tmp/{path[-1]}"
        s3_path = path[-1]
        if len(s3_path[3:]) > 1:
            s3_path = "/".join(path[3:])

        s3_client.download_file(
            Bucket=path[2], Key=f"{s3_path}", Filename=file_location
        )
        # Decrypt file content if it is encrypted
        try:
            with open(file_location) as file_object:
                decrypted_content = fernet_encrypt.decrypt(file_object.read())
            with open(file_location, "w") as file_object:
                file_object.write(decrypted_content)
        except (InvalidToken, UnicodeDecodeError):
            pass

        return file_location
