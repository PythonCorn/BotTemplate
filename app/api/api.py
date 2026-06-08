import logging

from fastapi import APIRouter, Header, Request
from starlette.responses import HTMLResponse

from app.infrastructure.fingerprint.html_text import HTML_TEXT
from app.infrastructure.fingerprint.schemas import Payload
from app.services.fingerprint_service import FingerprintService

router = APIRouter(prefix="/api", tags=["api"])

logger = logging.getLogger(__name__)


@router.get("/webapp", response_class=HTMLResponse)
async def get_captcha(request: Request):
    """
    Handles GET requests to the '/webapp' endpoint and returns an HTML response.

    Returns:
        HTML_TEXT (str): A string containing the HTML content to be rendered.

    """
    return HTML_TEXT


@router.post("/webapp")
async def post_fingerprint(
    payload: Payload,
    request: Request,
    x_telegram_init_data: str | None = Header(default=None),
):
    fingerprint_service = FingerprintService(x_telegram_init_data, payload, request)
    await fingerprint_service.handle()
    return {"status": "ok"}
