import asyncio
import logging
import signal

from aiogram.utils.i18n import I18n
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.bot.core.base import TelegramBot
from app.core.config import settings
from app.core.logger import setup_logging
from app.workers.backup.base import S3Backup
from app.workers.backup.postgres_dump import make_postgres_dump
from app.workers.backup.s3_client import S3Client
from app.workers.backup_worker import backup_worker
from app.workers.scheduler import create_scheduler

setup_logging()

logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    url=settings.POSTGRES_URI,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

I18N = I18n(path="app/locales", default_locale="ru")

BOT = TelegramBot(
    token=settings.BOT_TOKEN,
    session_factory=async_session_factory,
    i18n=I18N,
)


async def main():
    """
    Main entry point for initializing and running the asynchronous job scheduler.

    This function creates an instance of the asynchronous job scheduler, adds
    necessary jobs, manages graceful shutdown on receiving termination signals,
    and ensures proper cleanup of resources.

    Raises:
        Exception: Propagates exceptions raised during job scheduling, shutdown,
        or other asynchronous operations.

    """
    scheduler: AsyncIOScheduler = create_scheduler()

    postgres_file_name = await make_postgres_dump(
        postgres_name=settings.POSTGRES_DB,
        postgres_host=settings.POSTGRES_HOST,
        postgres_port=settings.POSTGRES_PORT,
        postgres_user=settings.POSTGRES_USER,
        postgres_password=settings.POSTGRES_PASSWORD,
        extra_name="example",
    )

    backup_client = S3Backup(
        s3_client=S3Client(
            bucket_name=settings.S3_BUCKET_NAME,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            region=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )
    )

    backup_worker(scheduler, backup_client, postgres_file_name, hours=1)
    await backup_client.send(file_path=postgres_file_name)

    scheduler.start()

    logger.info("Worker started")

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()

    logger.info("Worker stopping")

    scheduler.shutdown(wait=False)
    if BOT.session is not None:
        await BOT.session.close()


if __name__ == "__main__":
    asyncio.run(main())
