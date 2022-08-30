from aiogram import types

from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository, NeighborAyatsRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedAnswerByCallback, LoggedSourceCallback
from services.ayats.ayat_by_id import AyatById
from services.ayats.ayat_search import FavoriteAyats, SearchAnswer
from services.ayats.edit_markup import AyatFavoriteStatus, Markup
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from services.regular_expression import IntableRegularExpression
from settings import settings
from utlls import BotInstance, get_bot_instance

bot = get_bot_instance()


async def add_to_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки добавления аята в избранное.

    :param callback_query: app_types.CallbackQuery
    """
    intable_ayat_id = IntableRegularExpression(callback_query.data)
    chang_to = True
    await LoggedSourceCallback(
        AyatFavoriteStatus(
            chang_to,
            FavoriteAyatsRepository(database),
            intable_ayat_id,
            callback_query.from_user.id,
            Markup(
                BotInstance.get(),
                callback_query.from_user.id,
                callback_query.message.message_id,
                AyatSearchKeyboard(
                    AyatSearchWithNeighbors(
                        AyatById(
                            AyatRepository(database),
                            intable_ayat_id,
                        ),
                        NeighborAyatsRepository(database),
                    ),
                    FavoriteAyatsRepository(database),
                    callback_query.from_user.id,
                    AyatPaginatorCallbackDataTemplate.ayat_search_template,
                ),
            ),
        ),
        UpdatesLogRepository(
            NatsIntegration([]),
        ),
        callback_query,
    ).edit()


async def remove_from_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки удаления аята из избранного.

    :param callback_query: app_types.CallbackQuery
    """
    intable_ayat_id = IntableRegularExpression(callback_query.data)
    chang_to = False
    await LoggedSourceCallback(
        AyatFavoriteStatus(
            chang_to,
            FavoriteAyatsRepository(database),
            intable_ayat_id,
            callback_query.from_user.id,
            Markup(
                BotInstance.get(),
                callback_query.from_user.id,
                callback_query.message.message_id,
                AyatSearchKeyboard(
                    AyatSearchWithNeighbors(
                        AyatById(
                            AyatRepository(database),
                            intable_ayat_id,
                        ),
                        NeighborAyatsRepository(database),
                    ),
                    FavoriteAyatsRepository(database),
                    callback_query.from_user.id,
                    AyatPaginatorCallbackDataTemplate.ayat_search_template,
                ),
            ),
        ),
        UpdatesLogRepository(
            NatsIntegration([]),
        ),
        callback_query,
    ).edit()


async def favorite_ayat(callback_query: types.CallbackQuery):
    """Получить аят из избранного по кнопке.

    :param callback_query: app_types.CallbackQuery
    """
    ayat_search = AyatSearchWithNeighbors(
        FavoriteAyats(
            FavoriteAyatsRepository(database),
            callback_query.from_user.id,
            IntableRegularExpression(callback_query.data),
        ),
        FavoriteAyatsNeighborRepository(database, callback_query.from_user.id),
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
                AyatPaginatorCallbackDataTemplate.favorite_ayat_template,
            ),
        ),
    ).send()
