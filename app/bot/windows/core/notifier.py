import logging
from decimal import Decimal

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.i18n import I18n

from app.bot.windows.core import WindowMessage
from app.bot.windows.payment_window import PaymentWindows

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


class PaymentSuccessNotifier(Notifier):
    """
    Handles notifications related to successful payments.

    This class is responsible for notifying the relevant parties, such as administrators
    and users, about successful payment transactions. Notifications are sent using
    predefined window templates that include relevant information about the transaction.

    Attributes:
        i18n: An internationalization object used for generating localized messages.
    """

    async def notify_admin(
        self, user_id: int, username: str, admin_chat_id: int, amount: Decimal, provider: str
    ) -> None:
        """
        Sends a notification to an admin about the successful payment made by a user.

        This asynchronous method constructs and sends a message to the specified
        admin chat indicating a successful payment transaction. The notification
        includes details such as the username of the user, their user ID, the
        payment amount, and the payment provider.

        Args:
            user_id: The unique identifier of the user who completed the payment.
            username: The username of the user who completed the payment.
            admin_chat_id: The unique identifier of the chat where the admin
                notification will be sent.
            amount: The monetary amount of the payment made by the user.
            provider: The payment service provider used for the transaction.

        """
        window = PaymentWindows()
        await self.notify(
            chat_id=admin_chat_id,
            window=window.payment_success_admin(
                username=username, user_id=user_id, amount=amount, provider=provider, i18n=self.i18n
            ),
        )

    async def notify_user(
        self,
        user_id: int,
        amount: Decimal,
        locale: str = "ru",
    ) -> None:
        """
        Sends a notification to the user about a successful payment.

        This function generates a payment success notification message based on the provided
        amount and locale, and sends it to the specified user.

        Args:
            user_id (int): The unique identifier of the user to notify.
            amount (Decimal): The payment amount to be displayed in the notification.
            locale (str): The localization setting for the notification message. Defaults to "ru".

        Returns:
            None
        """
        window = PaymentWindows()
        await self.notify(
            chat_id=user_id,
            window=window.payment_success(amount=amount, i18n=self.i18n, locale=locale),
        )
