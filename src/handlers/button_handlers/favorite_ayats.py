from aiogram import types

from db.connection import database
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository, NeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import (
    LoggedSourceCallbackAyatSearchKeyboard,
)
from services.ayats.ayat_by_id import AyatById
from services.ayats.ayat_search import AyatFavoriteStatus, FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from services.regular_expression import IntableRegularExpression
from settings import settings
from utlls import get_bot_instance, BotInstance

bot = get_bot_instance()


async def add_to_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки добавления аята в избранное.

    :param callback_query: app_types.CallbackQuery
    """
    ayat_repository = AyatRepository(database)
    intable_ayat_id = IntableRegularExpression(r'\d+', callback_query.data)
    await AyatFavoriteStatus(
        FavoriteAyatsRepository(database),
        intable_ayat_id,
        callback_query.from_user.id,
    ).change(is_favorite=True)
    keyboard = await LoggedSourceCallbackAyatSearchKeyboard(
        AyatSearchKeyboard(
            AyatSearchWithNeighbors(
                AyatById(
                    ayat_repository,
                    intable_ayat_id,
                ),
                NeighborAyatsRepository(database),
            ),
            FavoriteAyatsRepository(database),
            callback_query.from_user.id,
            AyatPaginatorCallbackDataTemplate.ayat_search_template,
        ),
        UpdatesLogRepository(database),
        callback_query,
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
    ayat_repository = AyatRepository(database)
    intable_ayat_id = IntableRegularExpression(r'\d+', callback_query.data)
    await AyatFavoriteStatus(
        FavoriteAyatsRepository(database),
        intable_ayat_id,
        callback_query.from_user.id,
    ).change(is_favorite=False)
    keyboard = await LoggedSourceCallbackAyatSearchKeyboard(
        AyatSearchKeyboard(
            AyatSearchWithNeighbors(
                AyatById(
                    ayat_repository,
                    intable_ayat_id,
                ),
                NeighborAyatsRepository(database),
            ),
            FavoriteAyatsRepository(database),
            callback_query.from_user.id,
            AyatPaginatorCallbackDataTemplate.ayat_search_template,
        ),
        UpdatesLogRepository(database),
        callback_query,
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
    ayat_search = AyatSearchWithNeighbors(
        FavoriteAyats(
            FavoriteAyatsRepository(database),
            callback_query.from_user.id,
            IntableRegularExpression(r'\d+', callback_query.data),
        ),
        FavoriteAyatsNeighborRepository(database, callback_query.from_user.id),
    )
    await SearchAnswer(
        settings.DEBUG,
        BotInstance.get(),
        callback_query.from_user.id,
        ayat_search,
        AyatSearchKeyboard(
            ayat_search,
            FavoriteAyatsRepository(database),
            callback_query.from_user.id,
            AyatPaginatorCallbackDataTemplate.favorite_ayat_template,
        ),
    ).send()
