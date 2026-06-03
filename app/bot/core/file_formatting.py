import logging
from pathlib import Path

import aiofiles
from aiogram.types import BufferedInputFile, MaybeInaccessibleMessage, Message
from mypy.types import Any
from redis.asyncio import Redis

IMAGES_PATH = Path(__file__).parent.parent.parent / "static" / "images"

logger = logging.getLogger(__name__)


class FileFormatting:
    def __init__(self, redis: Redis, ttl: int = 60 * 60 * 24):
        self.path = IMAGES_PATH
        self.cache = redis
        self.ttl = ttl

    async def _read_file(self, filename: str) -> Any:
        path = self.path / filename
        async with aiofiles.open(file=path, mode="rb") as f:
            return await f.read()

    async def _get_file_id_from_cache(self, filename: str) -> str | None:
        value = await self.cache.get(filename)
        if value is not None and isinstance(value, bytes):
            logger.info(f"File {filename} found in cache")
            return value.decode("utf-8")
        if isinstance(value, str):
            logger.info(f"File {filename} found in cache")
            return value
        logger.info(f"File {filename} not found in cache")
        return None

    async def _add_file_id_to_cache(self, filename: str, file_id: str) -> None:
        await self.cache.set(filename, file_id, ex=self.ttl)
        logger.info(f"File {filename} {file_id} added to cache")

    async def get_photo(self, filename: str) -> str | BufferedInputFile:
        photo = await self._get_file_id_from_cache(filename)
        if photo is not None:
            return photo
        file = await self._read_file(filename)
        return BufferedInputFile(file, filename=filename)

    async def save_photo_in_cache(
        self, message: Message | MaybeInaccessibleMessage, filename: str
    ) -> None:
        if isinstance(message, Message) and message.photo is not None and len(message.photo) > 0:
            file_id = message.photo[-1].file_id
            await self._add_file_id_to_cache(filename, file_id)
            logger.info(f"Photo {file_id} saved in cache")
