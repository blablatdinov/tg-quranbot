import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.neighbor_ayats import (
    FavoriteAyatsNeighborRepository,
    NeighborAyatsRepository,
    TextSearchNeighborAyatsRepository,
)
from repository.podcast import PodcastRepository
from repository.prayer_time import PrayerTimeRepository
from repository.user import UserRepository
from services.ayat import AyatsService
from services.ayats.ayat_search import AyatSearchByText, FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatBySuraAyatNum, AyatBySuraAyatNumWithNeighbors
from services.podcast import PodcastAnswer, PodcastService
from services.prayer_time import PrayerTimes, UserHasNotCityExistsSafeAnswer, UserPrayerTimes, UserPrayerTimesAnswer


async def ayat_search_handler(message: types.Message):
    """Поиск по аятам по номеру суры и аята.

    :param message: types.Message
    """
    async with db_connection() as connection:
        ayat_repository = AyatRepository(connection)
        ayat_search = AyatBySuraAyatNumWithNeighbors(
            AyatBySuraAyatNum(
                ayat_repository,
                message.text,
            ),
            NeighborAyatsRepository(connection),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                ayat_repository,
                message.chat.id,
                AyatPaginatorCallbackDataTemplate.ayat_search_template,
            )
        ).transform()
        await answer.send(message.chat.id)


async def prayer_times_handler(message: types.Message):
    """Получить времена намаза.

    :param message: types.Message
    """
    async with db_connection() as connection:
        answer = await UserHasNotCityExistsSafeAnswer(
            UserPrayerTimesAnswer(
                UserPrayerTimes(
                    PrayerTimes(
                        prayer_times_repository=PrayerTimeRepository(connection),
                        user_repository=UserRepository(connection),
                        chat_id=message.chat.id,
                    ),
                    datetime.datetime.now(),
                ),
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


async def ayats_text_search(message: types.Message, state: FSMContext):
    """Поиск аятов по тексту.

    :param message: types.Message
    """
    async with db_connection() as connection:
        # query = message.text
        query = 'Аллах'
        await state.update_data(search_query=query)
        answer = await SearchAnswer(
            AyatSearchByText(
                AyatsService(
                    AyatRepository(connection),
                    message.chat.id,
                ),
                query,
                state,
            ),
            TextSearchNeighborAyatsRepository(connection, query),
        ).transform()

        await answer.send(message.chat.id)
