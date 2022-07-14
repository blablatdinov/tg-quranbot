from aiogram import Dispatcher
from aiogram.dispatcher import filters

from constants import AYAT_SEARCH_INPUT_REGEXP, GET_PRAYER_TIMES_REGEXP, PODCAST_BUTTON
from handlers import button_handlers, command_handlers, location, message_handlers, search_handler


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    _register_message_handlers(dp)
    _register_button_handlers(dp)
    dp.register_inline_handler(search_handler.inline_search_handler)


def _register_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(location.location_handler, content_types=['location'])
    dp.register_message_handler(command_handlers.start_handler, commands=['start'])
    dp.register_message_handler(
        message_handlers.ayat_search_by_sura_ayat_num_handler, filters.Regexp(AYAT_SEARCH_INPUT_REGEXP),
    )
    dp.register_message_handler(message_handlers.prayer_times_handler, filters.Regexp(GET_PRAYER_TIMES_REGEXP))
    dp.register_message_handler(message_handlers.podcasts_handler, filters.Regexp(PODCAST_BUTTON))
    dp.register_message_handler(message_handlers.favorite_ayats_list, filters.Regexp('Избранное'))
    dp.register_message_handler(message_handlers.ayats_text_search, filters.Regexp('Найти аят'))


def _register_button_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
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
    dp.register_callback_query_handler(
        button_handlers.favorite_ayat,
        lambda callback: callback.data and callback.data.startswith('get_favorite_ayat'),
    )
