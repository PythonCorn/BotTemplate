from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ExampleWindow:
    @staticmethod
    def start(username: str | None = None) -> dict:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text=_("Example button"),
            callback_data="example_callback",
        )
        return {
            "caption": _("Example message {username}").format(username=username),
            "reply_markup": keyboard.adjust(1).as_markup(),
        }
