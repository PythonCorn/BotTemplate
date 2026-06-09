from aiogram.types import WebAppInfo

from app.bot.windows.core.base_window import BaseWindow
from app.bot.windows.core.window_message import WindowMessage
from app.bot.windows.payment_window import PaymentCallbackData


class StartWindows(BaseWindow):
    def start(
        self, public_url: str, web_app_path: str, username: str | None = None
    ) -> WindowMessage:
        keyboard = self.inline_keyboard()
        keyboard.button(
            text=self._("Пополнить счет"),
            callback_data=PaymentCallbackData(),
        )
        keyboard.button(
            text=self._("WebApp"),
            web_app=WebAppInfo(url=f"{public_url}{web_app_path}"),
        )
        keyboard.button(
            text=self._("Проверка работы i18n"),
            callback_data="i18n",
        )
        keyboard.button(
            text=self._("Какой-то текст {username}", username=username),
            callback_data="test",
        )
        return WindowMessage(
            caption=self._("Example message {username}", username=username),
            reply_markup=keyboard.adjust(1).as_markup(),
            photo_filename="example.png",
        )
