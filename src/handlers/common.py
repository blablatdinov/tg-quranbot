from aiogram import Dispatcher, types
from aiogram.dispatcher import filters

from constants import AYAT_SEARCH_INPUT_REGEXP, GET_PRAYER_TIMES_REGEXP
from db import db_connection
from repository.prayer_time import PrayerTimeRepository
from repository.user import UserRepository
from services.prayer_time import UserPrayerTimes
from services.register_user import get_register_user_instance


async def start_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: types.Message
    """
    async with db_connection() as connection:
        register_user = await get_register_user_instance(connection, message.chat.id, message.text)
        answers = await register_user.register()
        await answers.send()


async def ayat_search_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: types.Message
    """
    async with db_connection() as connection:
        register_user = await get_register_user_instance(connection, message.chat.id, message.text)
        answers = await register_user.register()
        await answers.send()


async def prayer_times_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: types.Message
    """
    async with db_connection() as connection:
        prayers = await UserPrayerTimes(
            prayer_times_repository=PrayerTimeRepository(connection),
            user_repository=UserRepository(connection),
            chat_id=message.chat.id,
        ).get()
        await prayers.format_to_answer().send(message.chat.id)


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(start_handler, commands=['start'])
    dp.register_message_handler(ayat_search_handler, filters.Regexp(AYAT_SEARCH_INPUT_REGEXP))
    dp.register_message_handler(prayer_times_handler, filters.Regexp(GET_PRAYER_TIMES_REGEXP))
