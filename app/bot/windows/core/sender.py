import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    TelegramObject,
    Update,
)

from app.bot.core.file_formatting import FileFormatting
from app.bot.windows.core.base import WindowMessage

logger = logging.getLogger(__name__)


class Sender:
    """
    Handles event management and message formatting for sending and editing messages.

    This class serves as an abstraction for managing various types of Telegram events,
    including messages and callback queries. It provides functionality to send or
    update messages with text, photos, and captions, and integrates a formatting
    mechanism for structured content handling.

    Attributes:
        event (TelegramObject | Update): The event instance, resolved to a message
            or callback query, based on the type of the input event.
        formatter (FileFormatting): An instance of the FileFormatting class used
            to process and format message-related data.
    """

    def __init__(self, event: TelegramObject | Update, formatter: FileFormatting) -> None:
        """
        Initializes an instance of the class to process a Telegram event with a specified
        formatter. This handles both `Update` objects and generic `TelegramObject`.

        Attributes:
        event (TelegramObject | Update): Represents the event data from Telegram, either
            a message or callback query if the event is of type `Update`.
        formatter (FileFormatting): Specifies the file formatting utility used for processing.

        Args:
        event (TelegramObject | Update): The Telegram event to initialize the instance with.
        formatter (FileFormatting): The formatter instance to be used for processing.

        """
        self.event: Message | CallbackQuery | None = None

        if isinstance(event, Update):
            if event.message is not None:
                self.event = event.message
            elif event.callback_query is not None:
                self.event = event.callback_query

        logger.debug("Event: %s", event)
        self.formatter = formatter
        self._is_answer = False

    async def send(
        self, window: WindowMessage, *, alert: WindowMessage | None = None
    ) -> Message | bool | None:
        """
        Asynchronously sends a window message, handling different types of events and updating
        or creating message content accordingly. The method intelligently determines whether
        to send text, photo, or caption based on the provided `window` and `alert`.

        Args:
            window (WindowMessage): The window message object containing the details of the
                                    message to be sent or updated.
            alert (WindowMessage | None, optional): An optional alert window message object
                                                    to be used during editing. Defaults to None.

        Returns:
            Message | bool | None: Returns a `Message` object if the operation was successful,
                                   a boolean if the operation returned a status, or None if
                                   no message could be sent or updated.
        """
        logger.debug("Window: %s", window)
        if window.photo_filename is not None:
            if isinstance(self.event, Message):
                return await self.answer_photo(window)
            return await self.edit_photo(window, alert=alert)
        if isinstance(self.event, Message):
            return await self.answer_text(window)
        if (
            isinstance(self.event, CallbackQuery)
            and isinstance(self.event.message, Message)
            and self.event.message.caption is not None
        ):
            return await self.edit_caption(window, alert=alert)
        return await self.edit_text(window, alert=alert)

    async def answer_text(self, window: WindowMessage) -> Message | bool | None:
        """
        Handles answering a text message with an optional reply markup.

        Raises a ValueError if the 'text' attribute of the 'window' parameter is None.
        The method also returns None if the 'message' attribute is not set.

        Parameters:
            window (WindowMessage): The window message containing the text and an
                                    optional reply markup to be sent in the reply.

        Returns:
            Message | bool | None: The result of the 'answer' method of 'message',
                                   which could be a Message instance, a boolean value,
                                   or None, based on the 'answer' logic.

        Raises:
            ValueError: If the 'window.text' attribute is None.
        """
        message = self.message
        if message is None:
            return None
        if window.text is None:
            raise ValueError("Text is not set")

        return await message.answer(
            text=window.text,
            reply_markup=window.reply_markup,
        )

    async def answer_photo(self, window: WindowMessage) -> Message | bool | None:
        """
        Handles sending a photo message in response to a window message.

        This method attempts to retrieve a photo from the specified window and send
        it along with a caption and optional reply markup. If a message already
        exists, it updates the message with the provided photo. Optionally stores
        the photo message once it is sent successfully.

        Args:
            window (WindowMessage): The object containing the details for the photo,
            including caption, photo data, and reply markup.

        Returns:
            Message | bool | None: The message object if the photo message is sent
            successfully, False if saving the photo fails, or None if no message is available.
        """
        message = self.message
        photo = await self._get_photo(window)
        if message is not None:
            mes = await message.answer_photo(
                caption=window.caption, photo=photo, reply_markup=window.reply_markup
            )
            await self._save_photo(mes, window)
            return mes
        return None

    async def edit_photo(
        self, window: WindowMessage, *, alert: WindowMessage | None = None
    ) -> Message | bool | None:
        """
        Edits the photo of a given message window by utilizing Telegram's API.

        This method allows editing the media (photo) content of a message if
        certain criteria regarding the input parameters are met. It validates
        that the `photo_filename` attribute of the `window` parameter is properly
        set before proceeding. If applicable, reply markup is also checked to
        ensure it adheres to the required structure. If there is no intent to
        answer a query directly, an alert can be displayed. In case of issues
        with editing the media, it attempts to handle the situation gracefully.

        Parameters:
            window (WindowMessage): The message window containing the properties
                for the photo edit operation.
            alert (WindowMessage | None, optional): An optional window message
                to display as an alert. If not provided, no alert will be shown.

        Returns:
            Message | bool | None: The updated message if successful, False if
                a fallback action is taken, or None if the operation is not
                applicable.

        Raises:
            ValueError: If `photo_filename` in the `window` is not set or if the
                `reply_markup` is not of type InlineKeyboardMarkup.

        """
        if window.photo_filename is None:
            raise ValueError("Photo filename is not set")

        if isinstance(self.event, CallbackQuery) and isinstance(self.event.message, Message):
            if window.reply_markup is not None and not isinstance(
                window.reply_markup, InlineKeyboardMarkup
            ):
                raise ValueError("Reply markup must be an InlineKeyboardMarkup")
            if not self._is_answer:
                await self.alert(window=alert)
            try:
                return await self.event.message.edit_media(
                    media=InputMediaPhoto(
                        media=await self._get_photo(window),
                        caption=window.caption,
                    ),
                    reply_markup=window.reply_markup,
                )
            except TelegramBadRequest as error:
                logger.debug("Failed to edit message: %s", error)
                return await self._fallback_answer(window)
        return None

    async def edit_caption(
        self, window: WindowMessage, *, alert: WindowMessage | None = None
    ) -> Message | bool | None:
        """
        Edits the caption of a message associated with the current event, provided the event is a
        CallbackQuery and the message exists.

        Raises an alert if configured, ensures the reply_markup is of the appropriate type, and
        handles Telegram API errors gracefully.

        Parameters:
            window (WindowMessage): The new message details, including caption and reply markup.
            alert (WindowMessage | None): An optional alert to be displayed. Defaults to None.

        Returns:
            Message | bool | None: Returns the modified message if the caption was successfully edited;
            a fallback response if an error occurred during the edit; or None if the operation was
            skipped for other reasons.
        """
        if isinstance(self.event, CallbackQuery) and isinstance(self.event.message, Message):
            if not self._is_answer:
                await self.alert(window=alert)
            if window.reply_markup is not None and not isinstance(
                window.reply_markup, InlineKeyboardMarkup
            ):
                raise ValueError("Reply markup must be an InlineKeyboardMarkup")
            try:
                return await self.event.message.edit_caption(
                    caption=window.caption, reply_markup=window.reply_markup
                )
            except TelegramBadRequest as error:
                logger.debug("Failed to edit message: %s", error)
                return await self._fallback_answer(window)
        return None

    async def edit_text(
        self, window: WindowMessage, *, alert: WindowMessage | None = None
    ) -> Message | bool | None:
        """
        Edits the text content of a message within a window. Handles alerting if necessary
        and validates input types before updating the message. Falls back to handling
        arbitrary responses in case of failure.

        Parameters:
            window (WindowMessage): The window message object with the content to edit.
            alert (WindowMessage | None, optional): An optional alert window to show
                before editing. Defaults to None.

        Raises:
            ValueError: If the window's text is not set.
            ValueError: If the window's reply_markup is not of type InlineKeyboardMarkup.

        Returns:
            Message | bool | None: The edited message object, a fallback result,
                or None if editing is not possible.
        """
        if isinstance(self.event, CallbackQuery) and isinstance(self.event.message, Message):
            if not self._is_answer:
                await self.alert(window=alert)
            if window.text is None:
                raise ValueError("Text is not set")
            if window.reply_markup is not None and not isinstance(
                window.reply_markup, InlineKeyboardMarkup
            ):
                raise ValueError("Reply markup must be an InlineKeyboardMarkup")
            try:
                return await self.event.message.edit_text(
                    text=window.text, reply_markup=window.reply_markup
                )
            except TelegramBadRequest as error:
                logger.debug("Failed to edit message: %s", error)
                return await self._fallback_answer(window)
        return None

    async def alert(self, window: WindowMessage | None = None) -> bool:
        """
        Handles sending an alert in response to a callback query.

        Provides functionality to send an alert message or a default response
        if no window message is provided. The method verifies the event type
        before proceeding and ensures required attributes are set.

        Parameters:
            window (WindowMessage | None): Optional. The window message containing
            the text to show in the alert.

        Raises:
            ValueError: If the event is not a callback query.
            ValueError: If window.text is None when a window is provided.

        Returns:
            bool: True if the alert or answer message was successfully sent.
        """
        if not isinstance(self.event, CallbackQuery):
            raise ValueError("Event is not a callback query")
        if window is None:
            self._is_answer = True
            return await self.event.answer()
        if window.text is None:
            raise ValueError("Text is not set")
        self._is_answer = True
        return await self.event.answer(
            text=window.text,
            show_alert=True,
        )

    @property
    def message(self) -> Message | InaccessibleMessage | None:
        """
        Returns the message object based on the type of the current event.

        This property evaluates the available event data and extracts the associated
        message if the event is of type `Message` or `CallbackQuery`. If the event is
        not of either type, the property returns `None`.

        Returns:
            Message | InaccessibleMessage | None: The extracted message object if
            applicable, or None if no message is associated with the event.
        """
        message: Message | InaccessibleMessage | None = None
        if isinstance(self.event, Message):
            message = self.event
        elif isinstance(self.event, CallbackQuery):
            message = self.event.message
        return message

    async def _fallback_answer(self, window: WindowMessage) -> Message | bool | None:
        """
        Handles the fallback logic for sending an appropriate response to a given window message.

        If the message contains a photo filename, it delegates the response to the method
        responsible for handling photo messages. Otherwise, it delegates to the method
        responsible for handling text messages.

        Arguments:
            window (WindowMessage): The incoming window message to handle.

        Returns:
            Message | bool | None:
                The result of the response handling process.
                It can be a `Message` object if a response is sent successfully,
                a `bool` if the operation outcome is boolean-based,
                or `None` for cases where no response is applicable.
        """
        if window.photo_filename is not None:
            return await self.answer_photo(window)

        return await self.answer_text(window)

    async def _get_photo(self, window: WindowMessage):
        """
        Asynchronously retrieves a photo based on the filename provided in the
        WindowMessage instance.

        Parameters:
        window (WindowMessage): The WindowMessage instance containing the
        photo_filename attribute specifying the name of the photo to retrieve.

        Returns:
        Any: The formatted photo object retrieved by the formatter.

        Raises:
        ValueError: If the photo_filename attribute in the provided WindowMessage
        instance is None.
        """
        if window.photo_filename is None:
            raise ValueError("Photo filename is not set")
        return await self.formatter.get_photo(window.photo_filename)

    async def _save_photo(self, message: Message, window: WindowMessage):
        """
        Saves a photo to the local cache.

        This method is responsible for saving a photo from the given message to a
        specific filename. The photo is saved using the configured formatter's
        cache functionality. It ensures the required photo filename is provided
        before proceeding with the save operation.

        Raises:
            ValueError: If the photo filename is not set in the provided window.

        Args:
            message (Message): The message containing the photo to be saved.
            window (WindowMessage): The window object containing the target photo
                filename.
        """
        if window.photo_filename is None:
            raise ValueError("Photo filename is not set")
        await self.formatter.save_photo_in_cache(message, window.photo_filename)
