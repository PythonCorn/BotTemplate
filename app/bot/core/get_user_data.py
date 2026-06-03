from aiogram.types import CallbackQuery, Message, User


def get_user_data(event: Message | CallbackQuery) -> User:
    user: User | None = event.from_user
    if user is None:
        raise ValueError("User is not found")
    return user
