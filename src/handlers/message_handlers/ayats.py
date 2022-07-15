from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup

from constants import AYAT_SEARCH_INPUT_REGEXP
from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import (
    FavoriteAyatsNeighborRepository,
    NeighborAyatsRepository,
    TextSearchNeighborAyatsRepository,
)
from services.answer import Answer
from services.ayats.ayat_search import AyatNotFoundSafeAnswer, FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatBySuraAyatNum, AyatSearchWithNeighbors
from services.ayats.search_by_text import AyatSearchByText, AyatSearchByTextWithNeighbors


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


async def ayat_search_by_sura_ayat_num_handler(message: types.Message):
    """Поиск по аятам по номеру суры и аята.

    :param message: app_types.Message
    """
    async with db_connection() as connection:
        ayat_repository = AyatRepository(connection)
        ayat_search = AyatSearchWithNeighbors(
            AyatBySuraAyatNum(
                ayat_repository,
                message.text,
            ),
            NeighborAyatsRepository(connection),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                FavoriteAyatsRepository(connection),
                message.chat.id,
                AyatPaginatorCallbackDataTemplate.ayat_search_template,
            ),
        ).to_answer()
        await answer.send(message.chat.id)


class AyatSearchSteps(StatesGroup):
    """Состояния для поиска аятов."""

    insert_into_search_mode = State()


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
    async with db_connection() as connection:
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

    await AyatSearchSteps.insert_into_search_mode.set()
    await answer.send(message.chat.id)


def register_ayat_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(
        ayat_search_by_sura_ayat_num_handler, filters.Regexp(AYAT_SEARCH_INPUT_REGEXP), state='*',
    )
    dp.register_message_handler(favorite_ayats_list, filters.Regexp('Избранное'), state='*')
    dp.register_message_handler(ayats_text_search_button_handler, filters.Regexp('Найти аят'), state='*')
    dp.register_message_handler(ayats_text_search, state=AyatSearchSteps.insert_into_search_mode)
