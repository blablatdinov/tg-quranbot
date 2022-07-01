import re

from aiogram import types

from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.neighbor_ayats import NeighborAyatsRepository
from services.ayat import AyatsService
from services.ayat_search import AyatById, AyatFavoriteStatus, SearchAnswer
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
        reply_markup=keyboard,
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
        reply_markup=keyboard,
    )
