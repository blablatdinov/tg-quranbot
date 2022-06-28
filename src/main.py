from contextlib import asynccontextmanager

import asyncpg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters

from constants import AYAT_SEARCH_INPUT_REGEXP, GET_PRAYER_TIMES_REGEXP
from repository.admin_message import AdminMessageRepository
from repository.ayats import AyatRepository
from repository.prayer_time import PrayerTimeRepository
from repository.user import UserRepository
from services.ayat import AyatsService
from services.prayer_time import UserPrayerTimes
from services.register_user import RegisterUser
from services.start_message import get_start_message_query
from settings import settings
from utlls import get_bot_instance

bot = get_bot_instance()
dp = Dispatcher(bot)


async def get_register_user_instance(connection, chat_id: int, message: str) -> RegisterUser:
    """Возвращает объект для регистрации пользователя.

    :param chat_id: int
    :param connection: int
    :param message: str
    :returns: RegisterUser
    """
    return RegisterUser(
        user_repository=UserRepository(connection),
        admin_messages_repository=AdminMessageRepository(connection),
        ayat_service=AyatsService(
            AyatRepository(connection),
        ),
        chat_id=chat_id,
        start_message_meta=get_start_message_query(message),
    )


@asynccontextmanager
async def db_connection():
    """Контекстный менеджер для коннектов к БД.

    :yields: connection
    """
    connection = await asyncpg.connect(settings.DATABASE_URL)
    try:
        yield connection
    finally:
        await connection.close()


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: types.Message
    """
    async with db_connection() as connection:
        register_user = await get_register_user_instance(connection, message.chat.id, message.text)
        answers = await register_user.register()
        await answers.send()


@dp.message_handler(filters.Regexp(AYAT_SEARCH_INPUT_REGEXP))
async def ayat_search_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: types.Message
    """
    async with db_connection() as connection:
        register_user = await get_register_user_instance(connection, message.chat.id, message.text)
        answers = await register_user.register()
        await answers.send()


@dp.message_handler(filters.Regexp(GET_PRAYER_TIMES_REGEXP))
async def get_prayer_times_handler(message: types.Message):
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


@dp.message_handler(commands=['ping_db'])
async def ping_db(message: types.Message):
    """Проверка подключения к БД.

    :param message: types.Message
    """
    async with db_connection() as connection:
        ayat = await AyatsService(
            AyatRepository(connection),
        ).get_formatted_first_ayat()
        await message.answer(ayat)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
