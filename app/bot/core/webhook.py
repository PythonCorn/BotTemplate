# app/core/webhook.py
import logging

from app.core.config import settings
from app.core.container import Container
from app.ngrok.get_ngrok_url import get_ngrok_public_url

logger = logging.getLogger(__name__)


async def setup_telegram_webhook(container: Container) -> None:
    public_url = settings.PUBLIC_URL or await get_ngrok_public_url()

    if not public_url:
        raise RuntimeError("Public URL is not set")

    bot_webhook_url = f"{public_url}{settings.TELEGRAM_WEBHOOK_PATH}"

    await container.bot.delete_webhook(drop_pending_updates=True)
    await container.bot.set_webhook(
        url=bot_webhook_url,
        secret_token=settings.TELEGRAM_WEBHOOK_SECRET_TOKEN,
        ip_address=settings.TELEGRAM_WEBHOOK_IP_ADDRESS or None,
        allowed_updates=container.dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )

    logger.info("Telegram webhook configured: %s", bot_webhook_url)
