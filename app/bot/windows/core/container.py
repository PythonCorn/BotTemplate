from functools import cached_property

from aiogram.utils.i18n import I18n

from app.bot.windows.exception_windows import ExceptionWindows
from app.bot.windows.fingerprint_window import FingerprintWindow
from app.bot.windows.payment_window import PaymentWindows
from app.bot.windows.start_windows import StartWindows


class WindowsContainer:
    """
    Represents a container for managing various windows.

    This class provides access to specific window instances through cached properties.
    It serves as a centralized container to initialize and retrieve instances of
    windows, ensuring that each window is only instantiated once.
    """

    def __init__(self, i18n: I18n, locale: str = "ru") -> None:
        self.i18n = i18n
        self.locale: str = locale

    @cached_property
    def start(self) -> StartWindows:
        return StartWindows(i18n=self.i18n, locale=self.locale)

    @cached_property
    def payment(self) -> PaymentWindows:
        return PaymentWindows(i18n=self.i18n, locale=self.locale)

    @cached_property
    def exceptions(self) -> ExceptionWindows:
        return ExceptionWindows(i18n=self.i18n, locale=self.locale)

    @cached_property
    def fingerprint(self) -> FingerprintWindow:
        return FingerprintWindow(i18n=self.i18n, locale=self.locale)

    def __call__(self, locale: str):
        return WindowsContainer(i18n=self.i18n, locale=locale)
