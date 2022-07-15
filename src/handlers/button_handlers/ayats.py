from aiogram import types
from aiogram.dispatcher import FSMContext

from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import (
    FavoriteAyatsNeighborRepository,
    NeighborAyatsRepository,
    TextSearchNeighborAyatsRepository,
)
from services.ayats.ayat_by_id import AyatById
from services.ayats.ayat_search import AyatFavoriteStatus, FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from services.ayats.search_by_text import AyatSearchByTextAndId, AyatSearchByTextWithNeighbors
from services.regular_expression import IntableRegularExpression
from utlls import get_bot_instance

bot = get_bot_instance()


async def ayat_from_callback_handler(callback_query: types.CallbackQuery):
    """Получить аят из кнопки в клавиатуре под результатом поиска.

    :param callback_query: app_types.CallbackQuery
    """
    async with db_connection() as connection:
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
        await answer.send(callback_query.from_user.id)


async def add_to_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки добавления аята в избранное.

    :param callback_query: app_types.CallbackQuery
    """
    async with db_connection() as connection:
        ayat_repository = AyatRepository(connection)
        intable_ayat_id = IntableRegularExpression(r'\d+', callback_query.data)
        await AyatFavoriteStatus(
            FavoriteAyatsRepository(connection),
            intable_ayat_id,
            callback_query.from_user.id,
        ).change(is_favorite=True)
        keyboard = await AyatSearchKeyboard(
            AyatSearchWithNeighbors(
                AyatById(
                    ayat_repository,
                    intable_ayat_id,
                ),
                NeighborAyatsRepository(connection),
            ),
            FavoriteAyatsRepository(connection),
            callback_query.from_user.id,
            AyatPaginatorCallbackDataTemplate.ayat_search_template,
        ).generate()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard,
    )


async def remove_from_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки удаления аята из избранного.

    :param callback_query: app_types.CallbackQuery
    """
    async with db_connection() as connection:
        ayat_repository = AyatRepository(connection)
        intable_ayat_id = IntableRegularExpression(r'\d+', callback_query.data)
        await AyatFavoriteStatus(
            FavoriteAyatsRepository(connection),
            intable_ayat_id,
            callback_query.from_user.id,
        ).change(is_favorite=False)
        keyboard = await AyatSearchKeyboard(
            AyatSearchWithNeighbors(
                AyatById(
                    ayat_repository,
                    intable_ayat_id,
                ),
                NeighborAyatsRepository(connection),
            ),
            FavoriteAyatsRepository(connection),
            callback_query.from_user.id,
            AyatPaginatorCallbackDataTemplate.ayat_search_template,
        ).generate()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard,
    )


async def favorite_ayat(callback_query: types.CallbackQuery):
    """Получить аят из избранного по кнопке.

    :param callback_query: app_types.CallbackQuery
    """
    async with db_connection() as connection:
        ayat_search = AyatSearchWithNeighbors(
            FavoriteAyats(
                FavoriteAyatsRepository(connection),
                callback_query.from_user.id,
                IntableRegularExpression(r'\d+', callback_query.data),
            ),
            FavoriteAyatsNeighborRepository(connection, callback_query.from_user.id),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                FavoriteAyatsRepository(connection),
                callback_query.from_user.id,
                AyatPaginatorCallbackDataTemplate.favorite_ayat_template,
            ),
        ).to_answer()

    await answer.send(callback_query.from_user.id)


async def ayats_search_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопок для пролистывания по резултатам поиска.

    :param callback_query: app_types.CallbackQuery
    :param state: FSMContext
    """
    async with db_connection() as connection:
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

    await answer.send(callback_query.from_user.id)
