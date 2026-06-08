from fastapi import HTTPException, Request

from app.bot.windows.fingerprint_window import FingerprintWindow
from app.core.config import settings
from app.core.state import AppState, get_app_state
from app.database.models import Fingerprint
from app.database.unit_of_work import UnitOfWork
from app.infrastructure.fingerprint.build_fingerprint_hash import build_fingerprint_hash
from app.infrastructure.fingerprint.get_fingerprint import get_fingerprint
from app.infrastructure.fingerprint.schemas import Payload
from app.infrastructure.fingerprint.validate_init_data import validate_init_data
from app.services.fingerprint_match import FingerprintMatcherService


class FingerprintService:
    def __init__(self, x_telegram_init_data: str | None, payload: Payload, request: Request):
        if not x_telegram_init_data:
            raise HTTPException(status_code=401, detail="Telegram initData required")
        if not validate_init_data(x_telegram_init_data):
            raise HTTPException(status_code=403, detail="Invalid Telegram initData")
        self.fingerprint = get_fingerprint(x_telegram_init_data, request, payload)
        self.fingerprint_hash = build_fingerprint_hash(self.fingerprint)

        self.state: AppState = get_app_state(request)

    async def handle(self):
        async with UnitOfWork(self.state.session_factory) as uow:
            user = await uow.users.get_by_user_id(self.fingerprint.id)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

            existing_fp = await uow.fingerprints.get_by_hash_and_user_id(
                fingerprint_hash=self.fingerprint_hash,
                user_id=self.fingerprint.id,
            )

            if existing_fp is None:
                db_fingerprint = Fingerprint(
                    user_id=self.fingerprint.id,
                    fingerprint_hash=self.fingerprint_hash,
                    ip=self.fingerprint.ip,
                    user_agent=self.fingerprint.user_agent,
                    vendor=self.fingerprint.vendor,
                    renderer=self.fingerprint.renderer,
                    screen_width=self.fingerprint.screen_width,
                    screen_height=self.fingerprint.screen_height,
                    color_depth=self.fingerprint.color_depth,
                    device_pixel_ratio=self.fingerprint.device_pixel_ratio,
                    platform=self.fingerprint.platform,
                    device_platform=self.fingerprint.device_platform,
                    language=self.fingerprint.language,
                    timezone=self.fingerprint.timezone,
                )
                fp = await uow.fingerprints.add(db_fingerprint)
            else:
                fp = existing_fp
                fp.ip = self.fingerprint.ip
                fp.user_agent = self.fingerprint.user_agent

            user.is_check_fingerprint = True

            matcher = FingerprintMatcherService(uow)

            matches = await matcher.find_matches(
                fingerprint=fp,
                min_score=80,
            )
            await uow.commit()

            if settings.ADMIN_CHAT_ID is not None and len(matches) > 0:
                window = FingerprintWindow(i18n=self.state.bot.i18n)
                await self.state.bot.send_message_to_chat(
                    chat_id=settings.ADMIN_CHAT_ID,
                    message=window.get_scams(
                        user_id=self.fingerprint.id,
                        match_result=matches,
                    ),
                )
