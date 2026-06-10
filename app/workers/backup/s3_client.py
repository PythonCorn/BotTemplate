import logging
from contextlib import asynccontextmanager
from pathlib import Path

from aiobotocore.session import get_session

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str,
        endpoint_url: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "region_name": region,
            "endpoint_url": endpoint_url,
        }
        self.session = get_session()
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload(self, file_path: Path):
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=file_path.name,
                Body=file_path.read_bytes(),  # noqa: ASYNC240
            )
        logger.info(f"Backup sent to {self.endpoint_url}")
