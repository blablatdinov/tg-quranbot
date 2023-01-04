import httpx
from aioredis import Redis

from app_types.stringable import Stringable
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface
from services.user_state import UserState, UserStep


class ResetStateAnswer(TgAnswerInterface):
    """Декоратор для обнуления состояния пользователя."""

    def __init__(self, answer: TgAnswerInterface, redis: Redis):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param redis: Redis
        """
        self._origin = answer
        self._redis = redis

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        requests = await self._origin.build(update)
        await UserState(
            self._redis, int(TgChatId(update)),
        ).change_step(UserStep.nothing)
        return requests
