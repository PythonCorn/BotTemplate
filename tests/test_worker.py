from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.scheduler import create_scheduler


def test_create_scheduler():
    scheduler = create_scheduler()

    assert isinstance(scheduler, AsyncIOScheduler)
