from aiogram import Dispatcher
from aiogram.dispatcher import filters

from constants import AYAT_SEARCH_INPUT_REGEXP
from handlers.message_handlers.ayat_search_by_sura_ayat_num import ayat_search_by_sura_ayat_num_handler
from handlers.message_handlers.ayat_text_search import ayats_text_search, ayats_text_search_button_handler
from handlers.message_handlers.favorite_ayats import favorite_ayats_list
from states import AyatSearchSteps


def register_ayat_message_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(
        ayat_search_by_sura_ayat_num_handler, filters.Regexp(AYAT_SEARCH_INPUT_REGEXP), state='*',
    )
    dp.register_message_handler(favorite_ayats_list, filters.Regexp('Избранное'), state='*')
    dp.register_message_handler(ayats_text_search_button_handler, filters.Regexp('Найти аят'), state='*')
    dp.register_message_handler(ayats_text_search, state=AyatSearchSteps.insert_into_search_mode)
