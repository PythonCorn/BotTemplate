import logging

from fastapi import FastAPI

from app.api import health, webhook
from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.logger import setup_logging

setup_logging(
    level=settings.LOG_LEVEL,
    json_logs=settings.LOG_FORMAT == "json",
)

logger = logging.getLogger(__name__)
app = FastAPI(title="Bot Template", lifespan=lifespan)

app.include_router(router=webhook.router)
app.include_router(router=health.router)
