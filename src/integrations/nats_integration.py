import asyncio
import json

import nats
from quranbot_schema_registry.validate_schema import validate_schema

from repository.mailing import MailingRepository
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import Answer
from services.answers.spam_answer_list import SpamAnswerList, SavedSpamAnswerList


class NatsIntegration(object):

    def __init__(self, handlers):
        self._handlers = handlers

    async def _message_handler(self, event):
        event_dict = json.loads(event.data.decode())
        print(event_dict)
        validate_schema(event_dict, event_dict['event_name'], event_dict['event_version'])
        for handler in self._handlers:
            if handler.event_name == event_dict['event_name']:
                await handler.handle(event_dict['data'])
                await event.ack()

    async def receive(self):
        nats_client = await nats.connect("localhost")
        await nats_client.subscribe("foo", cb=self._message_handler)
        while True:
            await asyncio.sleep(1)


class MailingCreatedEvent(object):

    event_name = 'Mailing.Created'
    _users_repository: UsersRepositoryInterface

    def __init__(self, users_repository: UsersRepositoryInterface, mailing_repository: MailingRepository):
        self._users_repository = users_repository
        self._mailing_repository = mailing_repository

    async def handle(self, event):
        active_user_chat_ids = await self._users_repository.get_active_user_chat_ids()
        await SavedSpamAnswerList(
            SpamAnswerList(
                self._users_repository,
                *[
                    Answer(message=event['text'], chat_id=active_user_chat_id)
                    for active_user_chat_id in active_user_chat_ids
                ]
            ),
            self._mailing_repository,
        ).send()
