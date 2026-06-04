from aiogram.utils.i18n import gettext as _

from app.bot.windows.base import BaseWindow, WindowMessage


class ExampleWindow(BaseWindow):
    def start(self, username: str | None = None) -> WindowMessage:
        keyboard = self.get_empty_keyboard()
        keyboard.button(
            text=_("Пополнить счет"),
            callback_data="payment",
        )
        return WindowMessage(
            caption=_("Example message {username}").format(username=username),
            reply_markup=keyboard.adjust(1).as_markup(),
        )
