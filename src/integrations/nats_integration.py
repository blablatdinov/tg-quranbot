import asyncio
import json

import nats
from aiogram.utils.exceptions import MessageToDeleteNotFound
from loguru import logger
from quranbot_schema_registry.validate_schema import validate_schema

from repository.mailing import MailingRepository
from repository.update_log import UpdatesLogRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import Answer
from services.answers.spam_answer_list import SavedSpamAnswerList, SpamAnswerList
from utlls import get_bot_instance

bot = get_bot_instance()


class NatsIntegration(object):
    """Интеграция с nats."""

    def __init__(self, handlers: list):
        self._handlers = handlers

    async def receive(self) -> None:
        """Прием сообщений."""
        nats_client = await nats.connect('localhost')
        logger.info('Start handling events...')
        await nats_client.subscribe('foo', cb=self._message_handler)
        while True:  # noqa: WPS457
            await asyncio.sleep(1)

    async def _message_handler(self, event):
        event_dict = json.loads(event.data.decode())
        event_log_data = 'event_id={0} event_name={1}'.format(event_dict['event_name'], event_dict['event_id'])
        logger.info('Event {0} received'.format(event_log_data))
        try:
            validate_schema(event_dict, event_dict['event_name'], event_dict['event_version'])
        except TypeError as event_validate_error:
            logger.error('Validate {0} failed {1}'.format(event_log_data, str(event_validate_error)))
            return

        for event_handler in self._handlers:
            if event_handler.event_name == event_dict['event_name']:
                logger.info('Handling {0} event...'.format(event_log_data))
                await event_handler.handle_event(event_dict['data'])
                logger.info('Event {0} handled successful'.format(event_log_data))
                return

        logger.info('Event {0} skipped'.format(event_log_data))


class MailingCreatedEvent(object):
    """Класс обработывающий события о создании рассылки."""

    event_name = 'Mailing.Created'
    _users_repository: UsersRepositoryInterface

    def __init__(self, users_repository: UsersRepositoryInterface, mailing_repository: MailingRepository):
        self._users_repository = users_repository
        self._mailing_repository = mailing_repository

    async def handle_event(self, event):
        """Обработка события.

        :param event: dict
        """
        active_user_chat_ids = await self._users_repository.get_active_user_chat_ids()
        await SavedSpamAnswerList(
            SpamAnswerList(
                self._users_repository,
                *[
                    Answer(message=event['text'], chat_id=active_user_chat_id)
                    for active_user_chat_id in active_user_chat_ids
                ],
            ),
            self._mailing_repository,
        ).send()


class MessagesDeletedEvent(object):
    """Событие удаления сообщений."""

    event_name = 'Messages.Deleted'
    _messages_repository: UpdatesLogRepositoryInterface

    def __init__(self, messages_repository: UpdatesLogRepositoryInterface):
        self._messages_repository = messages_repository

    async def handle_event(self, event):
        """Обработка события.

        :param event: dict
        """
        messages = await self._messages_repository.get_messages(event['message_ids'])
        for message in messages:
            try:
                await bot.delete_message(message.chat_id, message.message_id)
            except MessageToDeleteNotFound:
                logger.warning('Message with id={0} chat_id={1} not found for deleting'.format(
                    message.message_id, message.chat_id,
                ))
