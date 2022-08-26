from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import TextSearchNeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.answer import DefaultKeyboard, TextAnswer
from services.answers.log_answer import LoggedSourceMessageAnswer
from services.ayats.ayat_search import AyatNotFoundSafeAnswer, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_text import AyatSearchByText, AyatSearchByTextWithNeighbors
from settings import settings
from states import AyatSearchSteps
from utlls import BotInstance


async def ayats_text_search_button_handler(message: types.Message):
    """Обработка кнопки для поиска аятов по тексту.

    :param message: app_types.Message
    """
    await AyatSearchSteps.insert_into_search_mode.set()
    await LoggedSourceMessageAnswer(
        UpdatesLogRepository(
            NatsIntegration([]),
        ),
        message,
        TextAnswer(
            BotInstance.get(),
            message.chat.id,
            'Введите слово для поиска:',
            DefaultKeyboard(),
        ),
    ).send()


async def ayats_text_search(message: types.Message, state: FSMContext):
    """Поиск аятов по тексту.

    :param message: app_types.Message
    :param state: FSMContext
    """
    query = message.text
    ayat_repository = AyatRepository(database)
    ayat_search = AyatSearchByTextWithNeighbors(
        AyatSearchByText(ayat_repository, query, state),
        TextSearchNeighborAyatsRepository(database, query),
    )
    await LoggedSourceMessageAnswer(
        UpdatesLogRepository(
            NatsIntegration([]),
        ),
        message,
        AyatNotFoundSafeAnswer(
            BotInstance.get(),
            message.chat.id,
            SearchAnswer(
                settings.DEBUG,
                BotInstance.get(),
                message.chat.id,
                ayat_search,
                AyatSearchKeyboard(
                    ayat_search,
                    FavoriteAyatsRepository(database),
                    message.chat.id,
                    AyatPaginatorCallbackDataTemplate.ayat_text_search_template,
                ),
            ),
        ),
    ).send()
