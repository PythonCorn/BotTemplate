import asyncio
import logging
import signal

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.core.setup_i18n import get_i18n
from app.core.config import settings
from app.core.logger import setup_logging
from app.workers.backup_worker import backup_worker
from app.workers.scheduler import create_scheduler

setup_logging()

logger = logging.getLogger(__name__)

I18N = get_i18n()

BOT = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


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
