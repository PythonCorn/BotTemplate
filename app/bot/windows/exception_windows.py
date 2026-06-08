from app.bot.windows.core.base_window import BaseWindow


class ExceptionWindows(BaseWindow):
    def exception_message(self):
        return self.message(text=self._("Произошла непредвиденная ошибка!"))
