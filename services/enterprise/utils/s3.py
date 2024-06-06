import os
import uuid

import boto3
from fastapi import UploadFile

from config import aws_s3_settings
from utils.encrypt import FernetEncrypt


class S3:
    def create_and_upload(self, content: str, file_name: str | None = None):
        fernet_encrypt = FernetEncrypt()
        # The file extension is hardcoded
        if not file_name:
            file_name = f"{str(uuid.uuid4())}.json"
        file_location = f"tmp/{file_name}"
        with open(file_location, "w") as file_object:
            file_object.write(fernet_encrypt.encrypt(content))

        return self._upload_file(file_location, file_name)

    def upload(self, file: UploadFile) -> str:
        fernet_encrypt = FernetEncrypt()
        file_name = f"{str(uuid.uuid4())}.{file.filename.split('.')[-1]}"
        file_location = f"tmp/{file_name}"

        with open(file_location, "w") as file_object:
            file_object.write(fernet_encrypt.encrypt(file.file.read().decode("utf-8")))

        return self._upload_file(file_location, file_name)

    def _upload_file(self, file_location: str, file_name: str) -> str:
        bucket_name = aws_s3_settings.s3_bucket_name
        # Upload the file
        s3_client: boto3.client = None
        if aws_s3_settings.s3_custom_endpoint:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_s3_settings.s3_aws_access_key_id,
                aws_secret_access_key=aws_s3_settings.s3_aws_secret_access_key,
                endpoint_url=aws_s3_settings.s3_custom_endpoint,
                aws_session_token=None,
            )
        else:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_s3_settings.s3_aws_access_key_id,
                aws_secret_access_key=aws_s3_settings.s3_aws_secret_access_key,
            )

        s3_client.upload_file(
            file_location, bucket_name, os.path.basename(file_location)
        )
        os.remove(file_location)
        return f"s3://{bucket_name}/{file_name}"
