import datetime

from aiogram import types

from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository, NeighborAyatsRepository
from repository.podcast import PodcastRepository
from repository.prayer_time import PrayerTimeRepository
from repository.user import UserRepository
from services.ayat import AyatsService
from services.ayat_search import AyatSearch, FavoriteAyats, SearchAnswer
from services.podcast import PodcastAnswer, PodcastService
from services.prayer_time import PrayerTimes, UserPrayerTimes, UserPrayerTimesAnswer


async def ayat_search_handler(message: types.Message):
    """Поиск по аятам по номеру суры и аята.

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
    """Получить времена намаза.

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
            ),
        ).to_answer()
        await answer.send(message.chat.id)


async def podcasts_handler(message: types.Message):
    """Получить случайный подкаст.

    :param message: types.Message
    """
    async with db_connection() as connection:
        answer = PodcastAnswer(
            await PodcastService(
                PodcastRepository(connection),
            ).get_random(),
        ).transform()

    await answer.send(message.chat.id)


async def favorite_ayats_list(message: types.Message):
    """Получить избранные аяты.

    :param message: types.Message
    """
    async with db_connection() as connection:
        answer = await SearchAnswer(
            FavoriteAyats(
                AyatsService(
                    AyatRepository(connection),
                    message.chat.id,
                ),
            ),
            FavoriteAyatsNeighborRepository(connection, message.chat.id),
        ).transform()
    await answer.send(message.chat.id)
