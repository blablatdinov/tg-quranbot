from aiogram import Dispatcher
from aiogram.dispatcher import filters

from constants import AYAT_SEARCH_INPUT_REGEXP, GET_PRAYER_TIMES_REGEXP, PODCAST_BUTTON
from handlers import button_handlers, message_handlers


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(message_handlers.start_handler, commands=['start'])
    dp.register_message_handler(message_handlers.ayat_search_handler, filters.Regexp(AYAT_SEARCH_INPUT_REGEXP))
    dp.register_message_handler(message_handlers.prayer_times_handler, filters.Regexp(GET_PRAYER_TIMES_REGEXP))
    dp.register_message_handler(message_handlers.podcasts_handler, filters.Regexp(PODCAST_BUTTON))

    dp.register_callback_query_handler(
        button_handlers.ayat_from_callback_handler,
        lambda callback: callback.data and callback.data.startswith('get_ayat'),
    )
    dp.register_callback_query_handler(
        button_handlers.add_to_favorite,
        lambda callback: callback.data and callback.data.startswith('add_to_favorite'),
    )
    dp.register_callback_query_handler(
        button_handlers.remove_from_favorite,
        lambda callback: callback.data and callback.data.startswith('remove_from_favorite'),
    )
    dp.register_callback_query_handler(
        button_handlers.mark_prayer_as_not_readed,
        lambda callback: callback.data and callback.data.startswith('mark_not_readed'),
    )
    dp.register_callback_query_handler(
        button_handlers.mark_prayer_as_readed,
        lambda callback: callback.data and callback.data.startswith('mark_readed'),
    )
