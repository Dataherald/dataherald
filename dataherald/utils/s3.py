import boto3

from dataherald.config import Settings


class S3:
    def __init__(self):
        self.settings = Settings()

    def download(self, path: str) -> str:
        path = path.split("/")
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.settings.require("s3_aws_access_key_id"),
            aws_secret_access_key=self.settings.require("s3_aws_secret_access_key"),
        )

        s3_client.download_file(
            Bucket=path[2], Key=f"{path[-1]}", Filename=f"tmp/{path[-1]}"
        )
        return f"tmp/{path[-1]}"
