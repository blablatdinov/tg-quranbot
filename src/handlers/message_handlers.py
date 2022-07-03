import datetime

from aiogram import types

from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.neighbor_ayats import NeighborAyatsRepository
from repository.prayer_time import PrayerTimeRepository
from repository.user import UserRepository
from services.ayat import AyatsService
from services.ayat_search import AyatSearch, SearchAnswer
from services.prayer_time import PrayerTimes, UserPrayerTimes, UserPrayerTimesAnswer
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
        answer = await SearchAnswer(
            AyatSearch(
                AyatsService(
                    AyatRepository(connection),
                    message.chat.id,
                ),
                message.text,
            ),
            NeighborAyatsRepository(connection),
        ).transform()
        await answer.send(message.chat.id)


async def prayer_times_handler(message: types.Message):
    """Ответ на команды: start.

    :param message: types.Message
    """
    async with db_connection() as connection:
        answer = await UserPrayerTimesAnswer(
            UserPrayerTimes(
                await PrayerTimes(
                    prayer_times_repository=PrayerTimeRepository(connection),
                    user_repository=UserRepository(connection),
                    chat_id=message.chat.id,
                ).get(),
                datetime.datetime.now(),
            )
        ).to_answer()
        await answer.send(message.chat.id)
