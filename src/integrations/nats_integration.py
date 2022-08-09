import datetime
import uuid
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


class MessageBrokerInterface(object):

    async def receive(self):
        raise NotImplementedError

    async def send(self, event_data, event_name, version):
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class NatsIntegration(MessageBrokerInterface):
    """Интеграция с nats."""

    _queue_name = 'default'

    def __init__(self, handlers: list):
        self._handlers = handlers

    async def send(self, event_data, event_name, version) -> None:
        """Отправить событие.

        :param event_data: dict
        :param event_name: str
        :param version: int
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_version': version,
            'event_name': event_name,
            'event_time': str(datetime.datetime.now()),
            'producer': 'quranbot-admin',
            'data': event_data,
        }
        validate_schema(event, event_name, version)
        nats_client = await nats.connect('localhost')

        logger.info('Publishing to queue: {0}, event_id: {1}, event_name: {2}'.format(
            self._queue_name, event['event_id'], event['event_name'],
        ))
        await nats_client.publish(self._queue_name, json.dumps(event).encode('utf-8'))
        logger.info('Event: id={0} name={1} to queue: {2} successful published'.format(
            event['event_id'], event['event_name'], self._queue_name,
        ))
        await nats_client.close()

    async def receive(self) -> None:
        """Прием сообщений."""
        nats_client = await nats.connect('localhost')
        logger.info('Start handling events...')
        logger.info('Receive evenst list: {0}'.format([event_handler.event_name for event_handler in self._handlers]))
        await nats_client.subscribe('default', cb=self._message_handler)
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
