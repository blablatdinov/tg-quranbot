from aiogram import types
from aiogram.dispatcher import FSMContext

from db import DBConnection
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import TextSearchNeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.answer import Answer
from services.answers.log_answer import LoggedAnswer, LoggedSourceMessageAnswerProcess
from services.ayats.ayat_search import AyatNotFoundSafeAnswer, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_text import AyatSearchByText, AyatSearchByTextWithNeighbors
from states import AyatSearchSteps


async def ayats_text_search_button_handler(message: types.Message):
    """Обработка кнопки для поиска аятов по тексту.

    :param message: app_types.Message
    """
    await AyatSearchSteps.insert_into_search_mode.set()
    await Answer(message='Введите слово для поиска:').send(message.chat.id)


async def ayats_text_search(message: types.Message, state: FSMContext):
    """Поиск аятов по тексту.

    :param message: app_types.Message
    :param state: FSMContext
    """
    async with DBConnection() as connection:
        query = message.text
        ayat_repository = AyatRepository(connection)
        ayat_search = AyatSearchByTextWithNeighbors(
            AyatSearchByText(ayat_repository, query, state),
            TextSearchNeighborAyatsRepository(connection, query),
        )
        answer = await AyatNotFoundSafeAnswer(
            SearchAnswer(
                ayat_search,
                AyatSearchKeyboard(
                    ayat_search,
                    FavoriteAyatsRepository(connection),
                    message.chat.id,
                    AyatPaginatorCallbackDataTemplate.ayat_text_search_template,
                ),
            ),
        ).to_answer()
        answer = LoggedSourceMessageAnswerProcess(
            UpdatesLogRepository(connection),
            message,
            LoggedAnswer(
                answer,
                UpdatesLogRepository(connection),
            ),
        )

    await answer.send(message.chat.id)
