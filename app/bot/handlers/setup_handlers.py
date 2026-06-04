from aiogram import Dispatcher

from app.bot.handlers import HANDLERS


def setup_handlers(dispatcher: Dispatcher):
    dispatcher.include_routers(*HANDLERS)
