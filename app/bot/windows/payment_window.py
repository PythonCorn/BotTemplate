from aiogram.filters.callback_data import CallbackData
from aiogram.utils.i18n import gettext as _

from app.bot.windows.core.base import BaseWindow
from app.bot.windows.core.keyboards import back_button
from app.infrastructure.payments import PaymentContainer
from app.infrastructure.payments.base import Invoice, PaymentProviderName


class PaymentCallbackData(CallbackData, prefix="payment"): ...


class PaymentProvidersCallbackData(CallbackData, prefix="p_p"):
    provider: PaymentProviderName


class PaymentWindows(BaseWindow):
    def start(self, payment_container: PaymentContainer):
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

    def attention(self):
        return self.message(text=_("Это предупреждение!"))

    def send_amount(self):
        keyboard = self.get_empty_keyboard()
        back_button(keyboard, callback_data=PaymentCallbackData())
        return self.message(
            caption=_("Отправьте сумму для пополнения в USD"),
            reply_markup=keyboard.adjust(1).as_markup(),
        )

    def create_invoice(self, invoice: Invoice):
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

    def invalid_operation(self):
        keyboard = self.get_empty_keyboard()
        back_button(keyboard, callback_data="start")
        return self.message(
            caption=_("Вы ввели неверное значение. Попробуйте еще раз!"),
            reply_markup=keyboard.adjust(1).as_markup(),
            photo_filename="example.png",
        )
