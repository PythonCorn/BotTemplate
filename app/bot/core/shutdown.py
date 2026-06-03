# app/core/shutdown.py
import logging

from app.core.container import Container
from app.database.session import async_engine

logger = logging.getLogger(__name__)


async def shutdown_container(container: Container) -> None:
    await container.bot.delete_webhook()

    if container.bot.session is not None:
        await container.bot.session.close()

    await container.redis.aclose()
    await async_engine.dispose()
    if container.payments is not None:
        await container.payments.close()
