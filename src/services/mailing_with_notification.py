import uuid

from aiogram import types

from app_types.mailing_interface import MailingInterface
from integrations.nats_integration import MessageBrokerInterface
from services.answers.spam_answer_list import SavedSpamAnswerList


class MailingWithNotification(MailingInterface):
    """Рассылка с уведомлением."""

    _saved_mailing: SavedSpamAnswerList
    _message_broker: MessageBrokerInterface

    def __init__(self, mailing: SavedSpamAnswerList, message_broker: MessageBrokerInterface):
        self._saved_mailing = mailing
        self._message_broker = message_broker

    async def send(self) -> list[types.Message]:
        """Отправить.

        :return: list[types.Message]
        """
        messages = await self._saved_mailing.send()
        await self._message_broker.send(
            {
                'public_id': str(uuid.uuid4()),
                'text': 'Рассылка #{0} завершена'.format(self._saved_mailing.mailing_num()),
            },
            'Notification.Created',
            1,
        )
        return messages
