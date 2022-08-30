from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import TextSearchNeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedAnswerByCallback
from services.ayats.ayat_search import SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_text import AyatSearchByTextAndId, AyatSearchByTextWithNeighbors
from services.regular_expression import IntableRegularExpression
from settings import settings
from utlls import BotInstance, get_bot_instance

bot = get_bot_instance()


async def ayats_search_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопок для пролистывания по резултатам поиска.

    :param callback_query: app_types.CallbackQuery
    :param state: FSMContext
    """
    state_data = await state.get_data()
    search_query = state_data['search_query']
    ayat_search = AyatSearchByTextWithNeighbors(
        AyatSearchByTextAndId(
            AyatRepository(database),
            search_query,
            IntableRegularExpression(callback_query.data),
        ),
        TextSearchNeighborAyatsRepository(database, search_query),
    )
    await LoggedAnswerByCallback(
        UpdatesLogRepository(
            NatsIntegration([]),
        ),
        callback_query,
        SearchAnswer(
            settings.DEBUG,
            BotInstance.get(),
            callback_query.from_user.id,
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                FavoriteAyatsRepository(database),
                callback_query.from_user.id,
                AyatPaginatorCallbackDataTemplate.ayat_text_search_template,
            ),
        ),
    ).send()
