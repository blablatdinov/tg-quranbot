import datetime
import re

from aiogram import types

from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository, NeighborAyatsRepository
from repository.prayer_time import PrayerTimeRepository
from repository.user import UserRepository
from services.ayat import AyatsService
from services.ayats.ayat_search import AyatById, AyatFavoriteStatus, FavoriteAyats, SearchAnswer
from services.prayer_time import PrayerTimes, UserPrayerStatus, UserPrayerTimes
from utlls import get_bot_instance

bot = get_bot_instance()


async def ayat_from_callback_handler(callback_query: types.CallbackQuery):
    """Получить аят из кнопки в клавиатуре под результатом поиска.

    :param callback_query: types.CallbackQuery
    """
    async with db_connection() as connection:
        ayat_id = int(re.search(r'\d+', callback_query.data).group(0))
        answer = await SearchAnswer(
            AyatById(
                AyatsService(
                    AyatRepository(connection),
                    callback_query.from_user.id,
                ),
                ayat_id,
            ),
            NeighborAyatsRepository(connection),
        ).transform()
        await answer.send(callback_query.from_user.id)


async def add_to_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки добавления аята в избранное.

    :param callback_query: types.CallbackQuery
    """
    ayat_id = int(re.search(r'\d+', callback_query.data).group(0))
    async with db_connection() as connection:
        ayat_favorite_status = AyatFavoriteStatus(
            ayat_service=AyatsService(AyatRepository(connection), callback_query.from_user.id),
            ayat_id=ayat_id,
            neighbors_ayat_repository=NeighborAyatsRepository(connection),
        )
        await ayat_favorite_status.change(is_favorite=True)
        keyboard = await ayat_favorite_status.generate_refreshed_keyboard()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard.generate(),
    )


async def remove_from_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки удаления аята из избранного.

    :param callback_query: types.CallbackQuery
    """
    ayat_id = int(re.search(r'\d+', callback_query.data).group(0))
    async with db_connection() as connection:
        ayat_favorite_status = AyatFavoriteStatus(
            ayat_service=AyatsService(AyatRepository(connection), callback_query.from_user.id),
            ayat_id=ayat_id,
            neighbors_ayat_repository=NeighborAyatsRepository(connection),
        )
        await ayat_favorite_status.change(is_favorite=False)
        keyboard = await ayat_favorite_status.generate_refreshed_keyboard()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard.generate(),
    )


async def mark_prayer_as_readed(callback_query: types.CallbackQuery):
    """Обработчик кнопки прочитанности аята.

    :param callback_query: types.CallbackQuery
    """
    user_prayer_id = int(re.search(r'\d+', callback_query.data).group(0))
    async with db_connection() as connection:
        user_prayer_status = UserPrayerStatus(
            prayer_times_repository=PrayerTimeRepository(connection),
            user_prayer_times=UserPrayerTimes(
                await PrayerTimes(
                    prayer_times_repository=PrayerTimeRepository(connection),
                    user_repository=UserRepository(connection),
                    chat_id=callback_query.from_user.id,
                ).get(),
                datetime.datetime.now(),
            ),
            user_prayer_id=user_prayer_id,
        )

        await user_prayer_status.change(True)
        keyboard = await user_prayer_status.generate_refresh_keyboard()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard,
    )


async def mark_prayer_as_not_readed(callback_query: types.CallbackQuery):
    """Обработчик кнопки прочитанности аята.

    :param callback_query: types.CallbackQuery
    """
    user_prayer_id = int(re.search(r'\d+', callback_query.data).group(0))
    async with db_connection() as connection:
        user_prayer_status = UserPrayerStatus(
            prayer_times_repository=PrayerTimeRepository(connection),
            user_prayer_times=UserPrayerTimes(
                await PrayerTimes(
                    prayer_times_repository=PrayerTimeRepository(connection),
                    user_repository=UserRepository(connection),
                    chat_id=callback_query.from_user.id,
                ).get(),
                datetime.datetime.now(),
            ),
            user_prayer_id=user_prayer_id,
        )

        await user_prayer_status.change(False)
        keyboard = await user_prayer_status.generate_refresh_keyboard()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard,
    )


async def favorite_ayat(callback_query: types.CallbackQuery):
    """Получить аят из избранного по кнопке.

    :param callback_query: types.CallbackQuery
    """
    ayat_id = int(re.search(r'\d+', callback_query.data).group(0))
    async with db_connection() as connection:
        answer = await SearchAnswer(
            FavoriteAyats(
                AyatsService(
                    AyatRepository(connection),
                    callback_query.from_user.id,
                ),
                ayat_id,
            ),
            FavoriteAyatsNeighborRepository(connection, callback_query.from_user.id),
        ).transform()
    await answer.send(callback_query.from_user.id)
