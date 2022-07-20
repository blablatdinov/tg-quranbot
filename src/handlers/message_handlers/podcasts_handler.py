from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters

from constants import PODCAST_BUTTON
from db import DBConnection
from repository.podcast import PodcastRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedAnswer, LoggedSourceMessageAnswer
from services.podcast import PodcastAnswer


async def podcasts_handler(message: types.Message, state: FSMContext):
    """Получить случайный подкаст.

    :param message: types.Message
    :param state: FSMContext
    """
    async with DBConnection() as connection:
        updates_log_repository = UpdatesLogRepository(connection)
        answer = LoggedSourceMessageAnswer(
            updates_log_repository,
            message,
            LoggedAnswer(
                await PodcastAnswer(
                    PodcastRepository(connection),
                ).to_answer(),
                updates_log_repository,
            ),
        )
        await answer.send(message.chat.id)

    await state.finish()


def register_podcasts_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(podcasts_handler, filters.Regexp(PODCAST_BUTTON), state='*')
