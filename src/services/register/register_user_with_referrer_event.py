import datetime

from integrations.nats_integration import MessageBrokerInterface
from services.answers.interface import AnswerInterface
from services.register.register_interface import RegisterInterface
from services.start_message import StartMessageInterface


class RegisterUserWithReferrerEvent(RegisterInterface):
    """Декоратор регистрации пользователя с рефералом для отправки события в шину."""

    def __init__(
        self,
        chat_id: int,
        origin: RegisterInterface,
        message_broker: MessageBrokerInterface,
        start_message: StartMessageInterface,
    ):
        self._chat_id = chat_id
        self._origin = origin
        self._message_broker = message_broker
        self._start_message = start_message

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
                'referrer_id': await self._start_message.referrer_id(),
                'date_time': datetime.datetime.now().isoformat(),
            },
            'User.Subscribed',
            1,
        )
        return answer
