import httpx

from app_types.stringable import Stringable
from exceptions.user import StartMessageNotContainReferrer
from integrations.nats_integration import SinkInterface
from integrations.tg.tg_answers import TgAnswerInterface
from repository.users.user import UserRepositoryInterface
from services.start.start_message import StartMessage


class StartWithEventAnswer(TgAnswerInterface):
    """Регистрация с отправкой события."""

    def __init__(self, answer: TgAnswerInterface, event_sink: SinkInterface, user_repo: UserRepositoryInterface):
        self._origin = answer
        self._event_sink = event_sink
        self._user_repo = user_repo

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            referrer_id = await StartMessage(update.message().text(), self._user_repo).referrer_chat_id()
        except StartMessageNotContainReferrer:
            referrer_id = None
        requests = await self._origin.build(update)
        await self._event_sink.send(
            {
                'user_id': update.chat_id(),
                'referrer_id': referrer_id,
                'date_time': str(update.message().date),
            },
            'User.Subscribed',
            1,
        )
        return requests
