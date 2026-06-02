import logging

from app.api import health, webhook
from app.api.factory import create_app
from app.core.config import settings
from app.core.logger import setup_logging

setup_logging(
    level=settings.LOG_LEVEL,
    json_logs=settings.LOG_FORMAT == "json",
)

logger = logging.getLogger(__name__)
app = create_app()

app.include_router(router=webhook.router)
app.include_router(router=health.router)
