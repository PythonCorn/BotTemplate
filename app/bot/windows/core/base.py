from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass(slots=True)
class WindowMessage:
    """
    Represents a message to be displayed in a window with optional attributes.

    The WindowMessage class serves as a structured container for constructing
    messages with text, captions, keyboards, and associated photo files.

    Attributes:
        text:
            The main text content of the message. None indicates no text.
        caption:
            An optional caption for the message. None indicates no caption.
        reply_markup:
            An optional keyboard layout for the message, using either an
            InlineKeyboardMarkup or ReplyKeyboardMarkup. None indicates no
            keyboard is provided.
        photo_filename:
            The filename of an optional photo to include in the message.
            None indicates no photo is associated.
    """

    text: str | None = None
    caption: str | None = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None
    photo_filename: str | None = None


class BaseWindow:
    """
    A base class for creating window-like elements in an application.

    This class provides utility methods to simplify the creation of
    keyboard layouts and window messages. It is designed to be a
    helper class for managing UI components such as inline keyboards
    and messages with optional text, captions, and media attachments.
    """

    @staticmethod
    def get_empty_keyboard() -> InlineKeyboardBuilder:
        """
        Provides a static method to generate an empty InlineKeyboardBuilder.

        Methods
        -------
        get_empty_keyboard()
            Creates and returns an instance of InlineKeyboardBuilder with no buttons.

        Returns
        -------
        InlineKeyboardBuilder
            An instance of InlineKeyboardBuilder with no buttons.
        """
        return InlineKeyboardBuilder()

    @staticmethod
    def message(
        text: str | None = None,
        caption: str | None = None,
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
        photo_filename: str | None = None,
    ) -> WindowMessage:
        """
        Static method for creating a `WindowMessage` instance with the provided
        message content, markup, and an optional photo filename.

        Parameters:
        text (str | None): The text message to be included, or None if not provided.
        caption (str | None): The caption for the message, or None if not provided.
        reply_markup (InlineKeyboardMarkup | ReplyKeyboardMarkup | None): The
            keyboard markup to be attached for user interaction. This can be of
            type InlineKeyboardMarkup, ReplyKeyboardMarkup or None if not provided.
        photo_filename (str | None): The filename of the photo, or None if not
            provided.

        Returns:
        WindowMessage: An instance of the `WindowMessage` class containing the
            provided data.
        """
        return WindowMessage(text, caption, reply_markup, photo_filename)
