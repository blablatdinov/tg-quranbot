from aiogram import types

from db import db_connection
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository
from services.ayats.ayat_search import FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors


async def favorite_ayats_list(message: types.Message):
    """Получить избранные аяты.

    :param message: app_types.Message
    """
    async with db_connection() as connection:
        favorite_ayats_repository = FavoriteAyatsRepository(connection)
        ayat_search = AyatSearchWithNeighbors(
            FavoriteAyats(
                favorite_ayats_repository,
                message.chat.id,
            ),
            FavoriteAyatsNeighborRepository(connection, message.chat.id),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                favorite_ayats_repository,
                message.chat.id,
                AyatPaginatorCallbackDataTemplate.favorite_ayat_template,
            ),
        ).to_answer()
    await answer.send(message.chat.id)
