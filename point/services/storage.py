import mimetypes
from contextlib import asynccontextmanager
import hashlib
import logging
from uuid import UUID


from aiobotocore.session import get_session, AioSession

from point.config import settings


class StorageService:
    bucket: str = settings.aws_bucket_name
    service_name: str = settings.aws_service_name
    config: dict[str, str]
    session: AioSession

    def __init__(self):
        self.config = {
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key,
            "endpoint_url": settings.aws_endpoint_url,
        }
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client(service_name=self.service_name, **self.config) as client:
            yield client

    async def put_raw_file(self, data: bytes, extension: str = "") -> str | None:
        try:
            async with self.get_client() as client:
                key = hashlib.md5(data).hexdigest()

                content_type, _ = mimetypes.guess_type("file" + extension)
                content_type = content_type or "application/octet-stream"

                response = await client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=data,
                    ContentType=content_type
                )
                if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    logging.error(f"Unexpected response while putting file in storage: {response}")
                    return None

                return key
        except Exception as e:
            logging.exception(f"Exception while putting file in storage: {e}")
            return None

    async def put_file(self, filename: str, data: bytes) -> str | None:
        extension = "." + filename.split(".")[-1]
        return await self.put_raw_file(data, extension=extension)

    async def delete_file(self, key: UUID) -> bool:
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket, Key=key)
                return True
        except Exception as e:
            logging.exception(f"Exception while putting file in storage: {e}")
            return False


storage = StorageService()
