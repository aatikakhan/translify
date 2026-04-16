from datetime import datetime
from pathlib import Path

import boto3

from app.config import settings


class StorageService:
    def __init__(self) -> None:
        self.use_local = settings.use_local_storage
        self.bucket = settings.aws_s3_bucket
        self.local_root = Path(settings.local_storage_dir)

        if self.use_local:
            self.local_root.mkdir(parents=True, exist_ok=True)
        else:
            self.client = boto3.client(
                "s3",
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id or None,
                aws_secret_access_key=settings.aws_secret_access_key or None,
            )

    def _build_key(self, folder: str, filename: str) -> str:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        safe_name = filename.replace(" ", "_")
        return f"{folder}/{ts}_{safe_name}"

    def upload_bytes(self, content: bytes, folder: str, filename: str) -> str:
        key = self._build_key(folder, filename)
        if self.use_local:
            output_file = self.local_root / key
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_bytes(content)
            return key

        self.client.put_object(Bucket=self.bucket, Key=key, Body=content)
        return key

    def read_bytes(self, key: str) -> bytes:
        if self.use_local:
            return (self.local_root / key).read_bytes()

        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()
