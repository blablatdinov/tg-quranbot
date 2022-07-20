from aiogram import types
from aiogram.dispatcher import FSMContext

from db import DBConnection
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedAnswer, LoggedSourceMessageAnswerProcess
from services.ayats.ayat_search import FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors


async def favorite_ayats_list(message: types.Message, state: FSMContext):
    """Получить избранные аяты.

    :param message: types.Message
    :param state: FSMContext
    """
    async with DBConnection() as connection:
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
        updates_log_repository = UpdatesLogRepository(connection)
        answer = LoggedSourceMessageAnswerProcess(
            updates_log_repository,
            message,
            LoggedAnswer(answer, updates_log_repository),
        )
        await answer.send(message.chat.id)

    await state.finish()
