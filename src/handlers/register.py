from aiogram import Dispatcher

from handlers import command_handlers, location, search_handler
from handlers.button_handlers.ayat_search_by_sura_ayat_num_pagination import ayat_from_callback_handler
from handlers.button_handlers.ayat_text_search import ayats_search_buttons
from handlers.button_handlers.favorite_ayats import add_to_favorite, favorite_ayat, remove_from_favorite
from handlers.button_handlers.prayers import mark_prayer_as_not_readed, mark_prayer_as_readed
from handlers.message_handlers.podcasts_handler import register_podcasts_message_handlers
from handlers.message_handlers.prayer_times import register_prayer_times_message_handlers
from handlers.message_handlers.register import register_ayat_message_handlers


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    register_prayer_times_message_handlers(dp)
    register_podcasts_message_handlers(dp)
    _register_message_handlers(dp)
    _register_button_handlers(dp)
    dp.register_inline_handler(search_handler.inline_search_handler)
    register_ayat_message_handlers(dp)


def _register_message_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(location.location_handler, content_types=['location'], state='*')
    dp.register_message_handler(command_handlers.start_handler, commands=['start'], state='*')


def _register_button_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_callback_query_handler(
        ayat_from_callback_handler,
        lambda callback: callback.data and callback.data.startswith('get_ayat'),
        state='*',
    )
    dp.register_callback_query_handler(
        add_to_favorite,
        lambda callback: callback.data and callback.data.startswith('add_to_favorite'),
        state='*',
    )
    dp.register_callback_query_handler(
        remove_from_favorite,
        lambda callback: callback.data and callback.data.startswith('remove_from_favorite'),
        state='*',
    )
    dp.register_callback_query_handler(
        mark_prayer_as_not_readed,
        lambda callback: callback.data and callback.data.startswith('mark_not_readed'),
        state='*',
    )
    dp.register_callback_query_handler(
        mark_prayer_as_readed,
        lambda callback: callback.data and callback.data.startswith('mark_readed'),
        state='*',
    )
    dp.register_callback_query_handler(
        favorite_ayat,
        lambda callback: callback.data and callback.data.startswith('get_favorite_ayat'),
        state='*',
    )
    dp.register_callback_query_handler(
        ayats_search_buttons,
        lambda callback: callback.data and callback.data.startswith('search_text_ayat'),
        state='*',
    )
