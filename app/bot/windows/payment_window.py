from aiogram.filters.callback_data import CallbackData
from aiogram.utils.i18n import gettext as _

from app.bot.windows.core.base import BaseWindow
from app.bot.windows.core.keyboards import back_button
from app.infrastructure.payments import PaymentContainer
from app.infrastructure.payments.base import PaymentProviderName


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
