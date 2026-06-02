import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.scheduler import create_scheduler

logger = logging.getLogger(__name__)


async def main():
    scheduler: AsyncIOScheduler = create_scheduler()

    # Add your jobs here
    # scheduler.add_job(
    #     my_task,
    #     trigger="interval",
    #     minutes=1,
    #     id="my_task",
    #     replace_existing=True,
    # )

    scheduler.start()

    logger.info("Worker started")

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()

    logger.info("Worker stopping")

    scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
