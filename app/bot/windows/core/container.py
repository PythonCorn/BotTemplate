from functools import cached_property

from app.bot.windows.example import ExampleWindow
from app.bot.windows.payment_window import PaymentWindows


class WindowsContainer:
    """
    Represents a container for managing various windows.

    This class provides access to specific window instances through cached properties.
    It serves as a centralized container to initialize and retrieve instances of
    windows, ensuring that each window is only instantiated once.
    """

    @cached_property
    def example(self) -> ExampleWindow:
        return ExampleWindow()

    @cached_property
    def payment(self) -> PaymentWindows:
        return PaymentWindows()
