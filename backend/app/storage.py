from pathlib import Path

from app.config import APP_ENV, FILE_STORAGE_PATH

BUCKET_NAME = "certificate"


class ObjectStorage:
    def __init__(self):
        self.local = APP_ENV == "test"
        if self.local:
            self.root = FILE_STORAGE_PATH / BUCKET_NAME
            self.root.mkdir(parents=True, exist_ok=True)
            return

        import boto3

        self.client = boto3.client(
            "s3",
            endpoint_url=self._required_env("AWS_ENDPOINT_URL_S3"),
            region_name=self._required_env("AWS_REGION"),
        )

    @staticmethod
    def _required_env(name: str) -> str:
        import os

        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"{name} is required for Neon Object Storage")
        return value

    def upload_bytes(self, key: str, contents: bytes, content_type: str) -> str:
        if self.local:
            destination = self.root / key
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(contents)
        else:
            self.client.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=contents,
                ContentType=content_type,
            )
        return key

    def download_bytes(self, key: str) -> bytes:
        if self.local:
            return (self.root / key).read_bytes()
        response = self.client.get_object(Bucket=BUCKET_NAME, Key=key)
        body = response["Body"]
        try:
            return body.read()
        finally:
            body.close()


storage = ObjectStorage()