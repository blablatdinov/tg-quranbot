import datetime

from integrations.nats_integration import MessageBrokerInterface
from services.answers.interface import AnswerInterface
from services.register.register_interface import RegisterInterface


class RegisterNewUserEvent(RegisterInterface):
    """Событие о регистрации нового пользователя."""

    def __init__(self, chat_id: int, origin: RegisterInterface, message_broker: MessageBrokerInterface):
        self._chat_id = chat_id
        self._origin = origin
        self._message_broker = message_broker

    async def can(self, chat_id: int) -> bool:
        """Проверка возможности регистрации.

        :param chat_id: int
        :return: bool
        """
        return await self._origin.can(chat_id)

    async def register(self, chat_id: int) -> AnswerInterface:
        """Регистрация.

        :param chat_id: int
        :return: AnswerInterface
        """
        answer = await self._origin.register(chat_id)
        await self._message_broker.send(
            {
                'user_id': self._chat_id,
                'date_time': datetime.datetime.now().isoformat(),
                'referrer_id': None,
            },
            'User.Subscribed',
            1,
        )
        return answer
