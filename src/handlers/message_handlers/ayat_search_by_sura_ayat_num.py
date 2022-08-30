from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedSourceMessageAnswer
from services.ayats.ayat_search import SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatBySuraAyatNum, AyatSearchWithNeighbors
from settings import settings
from utlls import BotInstance


async def ayat_search_by_sura_ayat_num_handler(message: types.Message, state: FSMContext):
    """Поиск по аятам по номеру суры и аята.

    :param message: app_types.Message
    :param state: FSMContext
    """
    ayat_repository = AyatRepository(database)
    ayat_search = AyatSearchWithNeighbors(
        AyatBySuraAyatNum(
            ayat_repository,
            message.text,
        ),
        NeighborAyatsRepository(database),
    )
    await LoggedSourceMessageAnswer(
        UpdatesLogRepository(
            NatsIntegration([]),
        ),
        message,
        SearchAnswer(
            settings.DEBUG,
            BotInstance.get(),
            message.chat.id,
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                FavoriteAyatsRepository(database),
                message.chat.id,
                AyatPaginatorCallbackDataTemplate.ayat_search_template,
            ),
        ),
    ).send()

    await state.finish()
