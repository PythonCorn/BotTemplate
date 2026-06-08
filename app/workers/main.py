import asyncio
import logging
import signal

from aiogram.utils.i18n import I18n
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.bot.core.base import TelegramBot
from app.core.config import settings
from app.core.logger import setup_logging
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

    # Add your jobs here
    # scheduler.add_job(
    #     my_task,
    #     trigger="interval",
    #     minutes=1,
    #     id="my_task",
    #     replace_existing=True,
    # )

    if settings.BACKUP_CHAT_ID is not None:
        backup_worker(scheduler, BOT)

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
