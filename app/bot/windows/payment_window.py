from decimal import Decimal

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _

from app.bot.windows.core.base import BaseWindow, WindowMessage
from app.bot.windows.core.keyboards import back_button
from app.infrastructure.payments import PaymentContainer
from app.infrastructure.payments.base import Invoice, PaymentProviderName


class PaymentCallbackData(CallbackData, prefix="payment"):
    """
    Handles callback data for payment operations.

    This class is designed to structure and manage callback data specific
    to payment functionalities. It extends the CallbackData class to
    leverage its base functionality while providing a specialized context
    for handling payment-related data.

    Attributes:
        prefix (str): The prefix used for identifying payment-specific
            callback data.
    """


class PaymentProvidersCallbackData(CallbackData, prefix="p_p"):
    """
    Represents callback data specifically for payment providers.

    This class is used to handle data associated with payment provider callbacks.
    It extends the CallbackData class and serves as a structured container for
    callback information related to payment providers.

    Attributes:
        provider (PaymentProviderName): The name of the payment provider associated
            with this callback.
    """

    provider: PaymentProviderName


class PaymentWindows(BaseWindow):
    """
    Handles interactions for payment windows in a user interface.

    This class provides methods to manage and display various payment-related interactions
    to the user, including selecting a payment provider, creating invoices, sending payment
    amounts, handling invalid operations, and providing feedback on payment statuses.

    Attributes:
        None
    """

    def start(self, payment_container: PaymentContainer) -> WindowMessage:
        """
        Creates a message window with a keyboard layout for selecting a payment provider.

        The function dynamically generates a keyboard with buttons for each available payment
        provider specified in the `payment_container`. Providers that are operational
        (as indicated by the `is_work` attribute) will have buttons created with their name
        and corresponding callback data. Additionally, a back button is added to the keyboard.

        Args:
            payment_container (PaymentContainer): A container object that holds a list of
                payment providers and their attributes, such as operational status and provider name.

        Returns:
            WindowMessage: A message object containing the caption and keyboard markup for
                selecting a payment provider.
        """
        keyboard = self.get_empty_keyboard()
        for provider in payment_container:
            if provider.is_work:
                keyboard.button(
                    text=provider.name_provider.value,
                    callback_data=PaymentProvidersCallbackData(provider=provider.name_provider),
                )
        back_button(keyboard)
        return self.message(
            caption=_("Выберите платежную систему:"), reply_markup=keyboard.adjust(1).as_markup()
        )

    def attention(self) -> WindowMessage:
        """
        Generates an attention message indicating a warning.

        This method is used to construct and return a warning message, represented
        by a `WindowMessage` object, with predefined text. It leverages
        localization/internationalization capabilities to ensure the message text
        can be presented in different languages.

        Returns:
            WindowMessage: A localized warning message instance.
        """
        return self.message(text=_("Это предупреждение!"))

    def send_amount(self) -> WindowMessage:
        """
        Sends a message prompting the user to input an amount for replenishment in USD.

        This method constructs and displays a message with a keyboard interface,
        providing the user with the ability to navigate back using a "back" button.
        The keyboard layout is adjusted for proper display.

        Returns:
            WindowMessage: The message object containing the prompt caption
            and the configured inline keyboard.
        """
        keyboard = self.get_empty_keyboard()
        back_button(keyboard, callback_data=PaymentCallbackData())
        return self.message(
            caption=_("Отправьте сумму для пополнения в USD"),
            reply_markup=keyboard.adjust(1).as_markup(),
        )

    def create_invoice(self, invoice: Invoice) -> WindowMessage:
        """
        Creates a payment message with an invoice, keyboard buttons for payment
        interaction, and an optional cancel button. Returns the constructed
        WindowMessage that can be sent to the user.

        Args:
            invoice (Invoice): The invoice object containing details for the
                payment, including the payment amount and payment URL.

        Returns:
            WindowMessage: The generated message object with the payment button,
            cancellation option, and a caption instructing the user to complete
            the payment.
        """
        keyboard = self.get_empty_keyboard()
        keyboard.button(
            text=_("Оплатить {amount} USD").format(amount=invoice.amount), url=invoice.pay_url
        )
        back_button(keyboard, text=_("Отмена"), callback_data="start")
        return self.message(
            caption=_("Оплатите сумму по кнопке ниже!"),
            reply_markup=keyboard.adjust(1).as_markup(),
            photo_filename="example.png",
        )

    def invalid_operation(self) -> WindowMessage:
        """
        Handles an invalid user operation and provides a message with corrective actions.

        Returns:
            WindowMessage: A message object containing the error caption, a back button for
                navigation, and an optional image to enhance the user experience.
        """
        keyboard = self.get_empty_keyboard()
        back_button(keyboard, callback_data="start")
        return self.message(
            caption=_("Вы ввели неверное значение. Попробуйте еще раз!"),
            reply_markup=keyboard.adjust(1).as_markup(),
            photo_filename="example.png",
        )

    def payment_success(self, amount: Decimal, i18n: I18n, locale: str = "ru") -> WindowMessage:
        """
        Generates a localized success message for a payment operation and returns it
        as a `WindowMessage` object.

        Args:
            amount (Decimal): The amount of money successfully added to the balance.
            i18n (I18n): An instance of the internationalization (i18n) utility.
            locale (str): The locale code used for message translation. Default is "ru".

        Returns:
            WindowMessage: A message object containing the localized confirmation text.
        """
        return self.message(
            text=i18n.gettext(
                "Ваш баланс успешно пополнен на сумму: {amount} USD", locale=locale
            ).format(amount=amount.quantize(Decimal("0.01")))
        )

    def payment_success_admin(
        self,
        username: str,
        user_id: int,
        amount: Decimal,
        provider: str,
        i18n: I18n,
    ) -> WindowMessage:
        """
        Generates an admin notification message for a successful payment, including
        details of the user and transaction.

        Args:
            username: The username of the user who made the payment.
            user_id: The Telegram ID of the user who made the payment.
            amount: The amount of the payment in USD as a Decimal.
            provider: The name of the payment system used for the transaction.
            i18n: An instance of the I18n class for internationalization.

        Returns:
            A WindowMessage object containing the payment success details formatted
            using the provided locale.
        """
        return self.message(
            text=i18n.gettext(
                "Пополнение баланса!\n\n"
                "Пользователь: @{username}\n"
                "Telegram ID: {user_id}\n\n"
                "Сумма: {amount} USD\n"
                "Платежная система: {provider}\n\n",
                locale="ru",
            ).format(
                username=username,
                user_id=user_id,
                amount=amount.quantize(Decimal("0.01")),
                provider=provider,
            )
        )
