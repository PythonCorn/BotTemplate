import logging
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.backup.base import BaseBackup

logger = logging.getLogger(__name__)


async def run_backup(backup: BaseBackup, file_path: Path) -> None:

    try:
        await backup.send(file_path=file_path)
        logger.info("PostgreSQL backup sent")
    except Exception as e:
        logger.exception("PostgreSQL backup failed %s", e, exc_info=True)


def backup_worker(scheduler: AsyncIOScheduler, backup: BaseBackup, file_path: Path, hours: int = 2):
    scheduler.add_job(
        run_backup,
        trigger="interval",
        hours=hours,
        args=(backup, file_path),
        id="backup_database",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
