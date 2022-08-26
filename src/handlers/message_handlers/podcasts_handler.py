from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters

from constants import PODCAST_BUTTON
from db.connection import database
from integrations.nats_integration import NatsIntegration
from repository.podcast import PodcastRepository
from repository.update_log import UpdatesLogRepository
from services.answers.log_answer import LoggedSourceMessageAnswer
from services.podcast import PodcastAnswer
from settings import settings
from utlls import BotInstance


async def podcasts_handler(message: types.Message, state: FSMContext):
    """Получить случайный подкаст.

    :param message: types.Message
    :param state: FSMContext
    """
    await LoggedSourceMessageAnswer(
        UpdatesLogRepository(NatsIntegration([])),
        message,
        PodcastAnswer(
            settings.DEBUG,
            message.chat.id,
            BotInstance.get(),
            PodcastRepository(database),
        ),
    ).send()
    await state.finish()


def register_podcasts_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(podcasts_handler, filters.Regexp(PODCAST_BUTTON), state='*')
