from aiogram import types

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedAnswerByCallback
from services.ayats.ayat_by_id import AyatById
from services.ayats.ayat_search import SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from services.regular_expression import IntableRegularExpression
from settings import settings
from utlls import BotInstance


async def ayat_from_callback_handler(callback_query: types.CallbackQuery):
    """Получить аят из кнопки в клавиатуре под результатом поиска.

    :param callback_query: app_types.CallbackQuery
    """
    ayat_search = AyatSearchWithNeighbors(
        AyatById(
            AyatRepository(database),
            IntableRegularExpression(callback_query.data),
        ),
        NeighborAyatsRepository(database),
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
                AyatPaginatorCallbackDataTemplate.ayat_search_template,
            ),
        ),
    ).send()
