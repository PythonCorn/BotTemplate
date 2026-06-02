from aiogram import Dispatcher, Router


def setup_bot_routers(*routers: Router, dispatcher: Dispatcher):
    if not routers:
        return
    dispatcher.include_routers(*routers)
