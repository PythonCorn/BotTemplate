import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)


async def make_postgres_dump() -> Path:
    """
    Creates a PostgreSQL database dump file asynchronously.

    This function generates a dump file for the configured PostgreSQL database
    using the `pg_dump` utility. The dump file is named based on the current
    timestamp and stored in the backup directory. The function ensures proper
    environment configuration for the `pg_dump` command, such as providing the
    database password through an environment variable. If the command fails,
    an error is raised with the details from standard error.

    Raises:
        RuntimeError: If the `pg_dump` command fails, the error message from
        standard error is raised.

    Returns:
        Path: The path to the created dump file.
    """
    filename = BACKUP_DIR / f"{settings.POSTGRES_DB}_{datetime.now():%Y-%m-%d_%H-%M-%S}.dump"

    cmd = [
        "pg_dump",
        "-h",
        settings.POSTGRES_HOST,
        "-p",
        str(settings.POSTGRES_PORT),
        "-U",
        settings.POSTGRES_USER,
        "-F",
        "c",
        "-f",
        str(filename),
        settings.POSTGRES_DB,
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = settings.POSTGRES_PASSWORD

    process = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(stderr.decode())

    return filename


async def send_backup(bot: Bot) -> None:
    """
    Sends a backup of the PostgreSQL database to a specified chat using a bot.

    This function generates a PostgreSQL database dump, sends the backup
    file to a designated chat through the given bot, and then removes the
    temporary file once the operation is complete.

    Args:
        bot (Bot): Instance of the bot used to send the backup file.

    Returns:
        None
    """
    file_path = await make_postgres_dump()
    if isinstance(settings.BACKUP_CHAT_ID, int):
        await bot.send_document(
            chat_id=settings.BACKUP_CHAT_ID,
            document=FSInputFile(file_path),
            caption=f"📦 PostgreSQL backup: {settings.POSTGRES_DB}",
        )

    file_path.unlink(missing_ok=True)


async def run_backup(bot: Bot) -> None:
    """
    Runs the backup process asynchronously.

    This function initiates the PostgreSQL backup process by calling the
    `send_backup` function, waits for its completion, and logs whether
    the backup was sent successfully or failed due to an exception.

    Args:
        bot: Bot instance used to send the backup.

    Raises:
        Exception: If an error occurs during the execution of the backup.
    """
    try:
        await send_backup(bot)
        logger.info("PostgreSQL backup sent")
    except Exception as e:
        logger.exception("PostgreSQL backup failed %s", e, exc_info=True)


def backup_worker(scheduler: AsyncIOScheduler, bot: Bot, hours: int = 2):
    """
    Schedules a periodic database backup task using the provided scheduler.

    This function schedules a job to run at regular intervals, defined by the
    specified number of hours, to back up the database. It uses the provided
    scheduler to handle job execution and ensures that only one instance of
    the job runs at a time. The backup task is executed by invoking the
    `run_backup` function with the specified bot instance as an argument.

    Args:
        scheduler (AsyncIOScheduler): The scheduler responsible for managing
            the backup job.
        bot (Bot): The bot instance that will be passed to the `run_backup`
            function for performing the backup.
        hours (int, optional): The interval in hours at which the backup job
            should run. Defaults to 2.

    """
    scheduler.add_job(
        run_backup,
        trigger="interval",
        hours=hours,
        args=(bot,),
        id="backup_database",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
