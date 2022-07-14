from aiogram import Dispatcher, types
from aiogram.dispatcher import filters

from constants import PODCAST_BUTTON
from db import db_connection
from repository.podcast import PodcastRepository
from services.podcast import PodcastAnswer, PodcastService


async def podcasts_handler(message: types.Message):
    """Получить случайный подкаст.

    :param message: app_types.Message
    """
    async with db_connection() as connection:
        answer = PodcastAnswer(
            await PodcastService(
                PodcastRepository(connection),
            ).get_random(),
        ).transform()

    await answer.send(message.chat.id)


def register_podcasts_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(podcasts_handler, filters.Regexp(PODCAST_BUTTON))
