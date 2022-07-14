from aiogram import types

from db import db_connection
from services.register_user import get_register_user_instance


async def start_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: app_types.Message
    """
    async with db_connection() as connection:
        register_user = await get_register_user_instance(connection, message.chat.id, message.text)
        answers = await register_user.register()
        await answers.send()
