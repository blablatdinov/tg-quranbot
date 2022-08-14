from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import DBConnection
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import TextSearchNeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedAnswer, LoggedSourceCallbackAnswerProcess
from services.ayats.ayat_search import SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_text import AyatSearchByTextAndId, AyatSearchByTextWithNeighbors
from services.regular_expression import IntableRegularExpression
from utlls import get_bot_instance

bot = get_bot_instance()


async def ayats_search_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопок для пролистывания по резултатам поиска.

    :param callback_query: app_types.CallbackQuery
    :param state: FSMContext
    """
    async with DBConnection() as connection:
        state_data = await state.get_data()
        search_query = state_data['search_query']
        ayat_search = AyatSearchByTextWithNeighbors(
            AyatSearchByTextAndId(
                AyatRepository(connection),
                search_query,
                IntableRegularExpression(r'\d+', callback_query.data),
            ),
            TextSearchNeighborAyatsRepository(connection, search_query),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                FavoriteAyatsRepository(connection),
                callback_query.from_user.id,
                AyatPaginatorCallbackDataTemplate.ayat_text_search_template,
            ),
        ).to_answer()
        answer = LoggedSourceCallbackAnswerProcess(
            UpdatesLogRepository(connection),
            callback_query,
            LoggedAnswer(answer, UpdatesLogRepository(connection)),
        )

        await answer.send(callback_query.from_user.id)
