import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bot.core.shutdown import shutdown_container
from app.bot.core.webhook import setup_telegram_webhook
from app.core.app_state import AppState
from app.core.bootstrap import create_container
from app.core.container import Container

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup started")

    container: Container = create_container()

    app.state.app_state = AppState(container=container)

    await setup_telegram_webhook(container=container)

    try:
        logger.info("Application startup completed")
        yield
    finally:
        logger.info("Application shutdown started")
        await shutdown_container(container=container)
        logger.info("Application shutdown completed")
