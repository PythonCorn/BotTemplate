from aiogram import Dispatcher
from aiogram.utils.i18n import I18n

from app.bot.middlewares.language_middleware import LanguageMiddleware


def get_i18n() -> I18n:
    """
    Gets an instance of the I18n class configured with the specified path and default locale.

    Returns:
        I18n: An instance of the I18n class initialized with the provided configuration.
    """
    return I18n(path="app/locales", default_locale="ru")


def setup_i18n(dispatcher: Dispatcher) -> I18n:
    """
    Configures internationalization (i18n) support for the given dispatcher.

    This function sets up i18n by retrieving the i18n instance through the
    `get_i18n()` function and attaching it to the dispatcher's middleware pipeline
    via a `LanguageMiddleware` instance.

    Args:
        dispatcher (Dispatcher): The dispatcher instance to which the
            internationalization middleware will be added.

    Returns:
        I18n: The configured i18n instance.
    """
    i18n = get_i18n()
    dispatcher.update.middleware(LanguageMiddleware(i18n=i18n))
    return i18n
