from aiogram.utils.i18n import gettext as _

from app.bot.windows.core.base_window import BaseWindow


class ExceptionWindows(BaseWindow):
    def exception_message(self):
        return self.message(text=_("Произошла непредвиденная ошибка!"))
