from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler


def create_scheduler():
    return AsyncIOScheduler(timezone=ZoneInfo("UTC"))
