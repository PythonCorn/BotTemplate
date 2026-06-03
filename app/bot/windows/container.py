from functools import cached_property

from app.bot.windows.example import ExampleWindow


class WindowsContainer:
    @cached_property
    def example(self) -> ExampleWindow:
        return ExampleWindow()
