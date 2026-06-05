from aiogram.types import WebAppInfo
from aiogram.utils.i18n import gettext as _

from app.bot.windows.core.base import BaseWindow, WindowMessage
from app.bot.windows.payment_window import PaymentCallbackData
from app.core.config import settings


class ExampleWindow(BaseWindow):
    def start(self, username: str | None = None) -> WindowMessage:
        keyboard = self.get_empty_keyboard()
        keyboard.button(
            text=_("Пополнить счет"),
            callback_data=PaymentCallbackData(),
        )
        keyboard.button(
            text=_("WebApp"),
            web_app=WebAppInfo(url=f"{settings.PUBLIC_URL}{settings.WEB_APP_PATH}"),
        )
        return WindowMessage(
            caption=_("Example message {username}").format(username=username),
            photo_filename="example.png",
            reply_markup=keyboard.adjust(1).as_markup(),
        )
