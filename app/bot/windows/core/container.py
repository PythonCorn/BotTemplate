from aiogram.utils.i18n import I18n

from app.bot.windows.exception_windows import ExceptionWindows
from app.bot.windows.fingerprint_window import FingerprintWindow
from app.bot.windows.payment_window import PaymentWindows
from app.bot.windows.start_windows import StartWindows


class Windows:
    def __init__(self, i18n: I18n | None = None, locale: str = "ru"):
        self.i18n = i18n
        self.locale = locale

    @property
    def start(self) -> StartWindows:
        return StartWindows(self)

    @property
    def payment(self) -> PaymentWindows:
        return PaymentWindows(self)

    @property
    def exceptions(self) -> ExceptionWindows:
        return ExceptionWindows(self)

    @property
    def fingerprint(self) -> FingerprintWindow:
        return FingerprintWindow(self)

    def __call__(self, locale: str) -> "Windows":
        return Windows(i18n=self.i18n, locale=locale)
