import logging

from fastapi import APIRouter, Header, HTTPException, Request
from starlette.responses import HTMLResponse

from app.bot.windows.core.notifier import NotifyScamUser
from app.core.app_state import AppState, get_app_state
from app.core.config import settings
from app.database.models import Fingerprint
from app.database.unit_of_work import UnitOfWork
from app.infrastructure.fingerprint.build_fingerprint_hash import build_fingerprint_hash
from app.infrastructure.fingerprint.get_fingerprint import get_fingerprint
from app.infrastructure.fingerprint.html_text import HTML_TEXT
from app.infrastructure.fingerprint.schemas import Payload
from app.infrastructure.fingerprint.validate_init_data import validate_init_data
from app.services.fingerprint_match import FingerprintMatcherService

router = APIRouter(prefix="/api", tags=["api"])

logger = logging.getLogger(__name__)


@router.get("/webapp", response_class=HTMLResponse)
async def get_captcha():
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
    """
    Handles the request to log a fingerprint associated with a Telegram user. This route
    validates Telegram initialization data, processes the provided payload, and persists
    or updates the fingerprint information in the database. Additionally, it performs
    fingerprint matching for potential fraud detection and notifies administrators if
    matches are found.

    Args:
        payload (Payload): Data structure containing the fingerprint details for processing.
        request (Request): The HTTP request object associated with the API call.
        x_telegram_init_data (str | None): Telegram initialization data passed via headers.
            This data is used for validation before processing. If not provided, raises an
            HTTP 401 exception.

    Raises:
        HTTPException: Raised with status 401 if `x_telegram_init_data` is missing or empty.
        HTTPException: Raised with status 403 if `x_telegram_init_data` fails validation.
        HTTPException: Raised with status 404 if the user associated with the fingerprint
            does not exist in the database.

    Returns:
        dict: A dictionary containing the status of the request and the generated fingerprint
        hash after processing.

    """
    if x_telegram_init_data is None or len(x_telegram_init_data) == 0:
        raise HTTPException(status_code=401, detail="Telegram initData required")

    if not validate_init_data(x_telegram_init_data):
        raise HTTPException(status_code=403, detail="Invalid Telegram initData")

    fingerprint = get_fingerprint(x_telegram_init_data, request, payload)
    fingerprint_hash = build_fingerprint_hash(fingerprint)

    state: AppState = get_app_state(request)

    async with UnitOfWork(state.container.session_factory) as uow:
        user = await uow.users.get_by_user_id(fingerprint.id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        existing_fp = await uow.fingerprints.get_by_hash_and_user_id(
            fingerprint_hash=fingerprint_hash,
            user_id=fingerprint.id,
        )
        if existing_fp is None:
            db_fingerprint = Fingerprint(
                user_id=fingerprint.id,
                fingerprint_hash=fingerprint_hash,
                ip=fingerprint.ip,
                user_agent=fingerprint.user_agent,
                vendor=fingerprint.vendor,
                renderer=fingerprint.renderer,
                screen_width=fingerprint.screen_width,
                screen_height=fingerprint.screen_height,
                color_depth=fingerprint.color_depth,
                device_pixel_ratio=fingerprint.device_pixel_ratio,
                platform=fingerprint.platform,
                device_platform=fingerprint.device_platform,
                language=fingerprint.language,
                timezone=fingerprint.timezone,
            )
            fp = await uow.fingerprints.add(db_fingerprint)
        else:
            fp = existing_fp
            fp.ip = fingerprint.ip
            fp.user_agent = fingerprint.user_agent

        matcher = FingerprintMatcherService(uow)

        matches = await matcher.find_matches(
            fingerprint=fp,
            min_score=80,
        )
        await uow.commit()

        if settings.ADMIN_CHAT_ID is not None and len(matches) > 0:
            notifier = NotifyScamUser(bot=state.container.bot, i18n=state.container.i18n)
            await notifier.notify_admins(
                chat_id=settings.ADMIN_CHAT_ID,
                user_id=fingerprint.id,
                match_result=matches,
            )

    return {
        "status": "ok",
        "fingerprint_hash": fingerprint_hash,
    }
