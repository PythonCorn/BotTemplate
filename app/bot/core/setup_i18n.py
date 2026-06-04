from aiogram import Dispatcher
from aiogram.utils.i18n import I18n

from app.bot.middlewares.language_middleware import LanguageMiddleware


def setup_i18n(dispatcher: Dispatcher):
    i18n = I18n(path="app/locales", default_locale="ru")
    dispatcher.update.middleware(LanguageMiddleware(i18n=i18n))
