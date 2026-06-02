from aiogram import Dispatcher, Router


def setup_bot_routers(*routers: Router, dispatcher: Dispatcher):
    dispatcher.include_routers(*routers)
