from aiogram import Dispatcher, types
from aiogram.dispatcher import filters

from constants import AYAT_SEARCH_INPUT_REGEXP
from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository, NeighborAyatsRepository
from services.ayats.ayat_search import FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatBySuraAyatNum, AyatSearchWithNeighbors


async def favorite_ayats_list(message: types.Message):
    """Получить избранные аяты.

    :param message: app_types.Message
    """
    async with db_connection() as connection:
        ayat_repository = AyatRepository(connection)
        ayat_search = AyatSearchWithNeighbors(
            FavoriteAyats(
                ayat_repository,
                message.chat.id,
            ),
            FavoriteAyatsNeighborRepository(connection, message.chat.id),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                ayat_repository,
                message.chat.id,
                AyatPaginatorCallbackDataTemplate.favorite_ayat_template,
            ),
        ).transform()
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
                ayat_repository,
                message.chat.id,
                AyatPaginatorCallbackDataTemplate.ayat_search_template,
            ),
        ).transform()
        await answer.send(message.chat.id)


def register_ayat_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(
        ayat_search_by_sura_ayat_num_handler, filters.Regexp(AYAT_SEARCH_INPUT_REGEXP),
    )
    dp.register_message_handler(favorite_ayats_list, filters.Regexp('Избранное'))


# async def ayats_text_search(message_handlers: types.Message, state: FSMContext):
#     """Поиск аятов по тексту.
#
#     :param message_handlers: app_types.Message
#     """
#     async with db_connection() as connection:
#         query = 'Аллах'
#         await state.update_data(search_query=query)
#         answer = await SearchAnswer(
#             AyatSearchByText(
#                 AyatsService(
#                     AyatRepository(connection),
#                     message_handlers.chat.id,
#                 ),
#                 query,
#                 state,
#             ),
#             TextSearchNeighborAyatsRepository(connection, query),
#         ).transform()
#
#         await answer.send(message_handlers.chat.id)
