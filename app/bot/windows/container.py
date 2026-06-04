from functools import cached_property

from app.bot.windows.example import ExampleWindow
from app.bot.windows.payment_window import PaymentWindows


class WindowsContainer:
    @cached_property
    def example(self) -> ExampleWindow:
        return ExampleWindow()

    @cached_property
    def payment(self) -> PaymentWindows:
        return PaymentWindows()
