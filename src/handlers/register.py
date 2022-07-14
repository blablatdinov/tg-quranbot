from aiogram import Dispatcher

from handlers import command_handlers, location, search_handler
from handlers.button_handlers.ayats import (
    add_to_favorite,
    ayat_from_callback_handler,
    favorite_ayat,
    remove_from_favorite,
)
from handlers.button_handlers.prayers import mark_prayer_as_not_readed, mark_prayer_as_readed
from handlers.message_handlers.ayats import register_ayat_message_handlers
from handlers.message_handlers.podcasts_handler import register_podcasts_message_handlers
from handlers.message_handlers.prayer_times import register_prayer_times_message_handlers


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    register_ayat_message_handlers(dp)
    register_prayer_times_message_handlers(dp)
    register_podcasts_message_handlers(dp)
    _register_message_handlers(dp)
    _register_button_handlers(dp)
    dp.register_inline_handler(search_handler.inline_search_handler)


def _register_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(location.location_handler, content_types=['location'])
    dp.register_message_handler(command_handlers.start_handler, commands=['start'])


def _register_button_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_callback_query_handler(
        ayat_from_callback_handler,
        lambda callback: callback.data and callback.data.startswith('get_ayat'),
    )
    dp.register_callback_query_handler(
        add_to_favorite,
        lambda callback: callback.data and callback.data.startswith('add_to_favorite'),
    )
    dp.register_callback_query_handler(
        remove_from_favorite,
        lambda callback: callback.data and callback.data.startswith('remove_from_favorite'),
    )
    dp.register_callback_query_handler(
        mark_prayer_as_not_readed,
        lambda callback: callback.data and callback.data.startswith('mark_not_readed'),
    )
    dp.register_callback_query_handler(
        mark_prayer_as_readed,
        lambda callback: callback.data and callback.data.startswith('mark_readed'),
    )
    dp.register_callback_query_handler(
        favorite_ayat,
        lambda callback: callback.data and callback.data.startswith('get_favorite_ayat'),
    )
