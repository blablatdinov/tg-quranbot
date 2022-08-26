from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository
from repository.update_log import UpdatesLogRepository
from services.answers.exceptions_safe_answer import ExceptionSafeAnswer
from services.answers.log_answer import LoggedSourceMessageAnswer
from services.ayats.ayat_search import FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from settings import settings
from utlls import BotInstance


async def favorite_ayats_list(message: types.Message, state: FSMContext):
    """Получить избранные аяты.

    :param message: types.Message
    :param state: FSMContext
    """
    await LoggedSourceMessageAnswer(
        UpdatesLogRepository(
            NatsIntegration([]),
        ),
        message,
        ExceptionSafeAnswer(
            SearchAnswer(
                settings.DEBUG,
                BotInstance.get(),
                message.chat.id,
                AyatSearchWithNeighbors(
                    FavoriteAyats(
                        FavoriteAyatsRepository(database),
                        message.chat.id,
                    ),
                    FavoriteAyatsNeighborRepository(database, message.chat.id),
                ),
                AyatSearchKeyboard(
                    AyatSearchWithNeighbors(
                        FavoriteAyats(
                            FavoriteAyatsRepository(database),
                            message.chat.id,
                        ),
                        FavoriteAyatsNeighborRepository(database, message.chat.id),
                    ),
                    FavoriteAyatsRepository(database),
                    message.chat.id,
                    AyatPaginatorCallbackDataTemplate.favorite_ayat_template,
                ),
            ),
            BotInstance.get(),
            message.chat.id,
        )
    ).send()

    await state.finish()
