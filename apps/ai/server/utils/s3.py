import os
import uuid

import boto3

from config import aws_s3_settings
from utils.encrypt import FernetEncrypt


class S3:
    def create_and_upload(self, content: str):
        fernet_encrypt = FernetEncrypt()
        bucket_name = "k2-core"
        # The file extension is hardcoded
        file_name = f"{str(uuid.uuid4())}.json"
        file_location = f"tmp/{file_name}"
        with open(file_location, "w") as file_object:
            file_object.write(fernet_encrypt.encrypt(content))

        # Upload the file
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
