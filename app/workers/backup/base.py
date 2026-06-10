from abc import ABC, abstractmethod
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile

from app.workers.backup.s3_client import S3Client


class BaseBackup(ABC):
    @abstractmethod
    async def send(self, file_path: Path): ...


class BotBackup(BaseBackup):
    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

    async def send(self, file_path: Path):
        await self.bot.send_document(
            chat_id=self.chat_id,
            document=FSInputFile(path=file_path, filename=file_path.name),
            caption=f"📦 PostgreSQL backup: {file_path.stem}",
        )


class S3Backup(BaseBackup):
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client

    async def send(self, file_path: Path):
        await self.s3_client.upload(file_path=file_path)
