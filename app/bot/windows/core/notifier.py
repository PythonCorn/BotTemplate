import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.i18n import I18n

from app.bot.windows.core import WindowMessage
from app.bot.windows.fingerprint_window import FingerprintWindow
from app.services.fingerprint_match import FingerprintMatchResult

logger = logging.getLogger(__name__)


class Notifier:
    """
    Handles notification responsibilities for sending messages via a bot.

    This class is designed to manage notifications, using a bot to send messages
    to the specified chat ID. It leverages the `Bot` instance for communication
    and the `I18n` instance for localization support as needed.

    Attributes:
        bot (Bot): An instance of the bot used for sending messages.
        i18n (I18n): An instance of the internationalization utility for handling
            localization of messages.
    """

    def __init__(self, bot: Bot, i18n: I18n) -> None:
        """
        Initializes the class with a bot instance and internationalization support.

        Args:
            bot: Instance of the Bot class to provide bot-related functionality.
            i18n: Instance of the I18n class to manage internationalization and
                localization.
        """
        self.bot = bot
        self.i18n = i18n

    async def notify(self, chat_id: int, window: WindowMessage) -> None:
        """
        Sends a notification message to the specified chat using the provided window
        message.

        This function asynchronously sends a message, including text and an optional
        reply markup, to the given chat ID. If the message text is not set, a
        ValueError is raised. In case of certain Telegram API errors, the errors are
        caught and logged as warnings.

        Args:
            chat_id (int): Unique identifier for the target chat.
            window (WindowMessage): Object containing the message text and optional
                reply markup.

        Raises:
            ValueError: If the text attribute of the window object is not set.
        """
        if window.text is None:
            raise ValueError("Text is not set")
        try:
            await self.bot.send_message(
                chat_id=chat_id, text=window.text, reply_markup=window.reply_markup
            )
        except (TelegramBadRequest, TelegramForbiddenError) as error:
            logger.warning("Failed to send message: %s", error)


class NotifyScamUser(Notifier):
    """
    Handles the process of notifying relevant parties about scam activity.

    This class inherits from the Notifier base class and provides functionality
    to notify administrators when a user is flagged for scam activities. It
    implements methods that leverage fingerprint matching results to identify
    scams and then send notifications accordingly.

    Attributes:
        None
    """

    async def notify_admins(
        self, chat_id: int, user_id: int, match_result: list[FingerprintMatchResult]
    ) -> None:
        """
        Notifies administrators about the match results associated with a specific user.

        This asynchronous method creates a fingerprint window and retrieves a list of scams
        based on the provided user ID and fingerprint match results. It then sends a notification
        to the specified chat.

        Args:
            chat_id (int): The ID of the chat where the notification should be sent.
            user_id (int): The unique identifier of the user for whom fingerprint matching results
                are being processed.
            match_result (list[FingerprintMatchResult]): A list containing the results of the
                fingerprint matching process.
        """
        window = FingerprintWindow()
        await self.notify(
            chat_id=chat_id,
            window=window.get_scams(
                user_id=user_id,
                match_result=match_result,
            ),
        )
