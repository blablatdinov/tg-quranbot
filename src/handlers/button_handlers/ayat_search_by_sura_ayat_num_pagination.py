from aiogram import types

from db import DBConnection
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedAnswer, LoggedSourceCallbackAnswerProcess
from services.ayats.ayat_by_id import AyatById
from services.ayats.ayat_search import SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from services.regular_expression import IntableRegularExpression


async def ayat_from_callback_handler(callback_query: types.CallbackQuery):
    """Получить аят из кнопки в клавиатуре под результатом поиска.

    :param callback_query: app_types.CallbackQuery
    """
    async with DBConnection() as connection:
        ayat_search = AyatSearchWithNeighbors(
            AyatById(
                AyatRepository(connection),
                IntableRegularExpression(r'\d+', callback_query.data),
            ),
            NeighborAyatsRepository(connection),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                FavoriteAyatsRepository(connection),
                callback_query.from_user.id,
                AyatPaginatorCallbackDataTemplate.ayat_search_template,
            ),
        ).to_answer()
        updates_log_repository = UpdatesLogRepository(connection)
        answer = LoggedSourceCallbackAnswerProcess(
            updates_log_repository,
            callback_query,
            LoggedAnswer(answer, updates_log_repository),
        )
        await answer.send(callback_query.from_user.id)
