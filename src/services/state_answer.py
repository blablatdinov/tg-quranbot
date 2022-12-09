import httpx
from aioredis import Redis

from app_types.stringable import Stringable
from integrations.tg.tg_answers import TgAnswerInterface
from services.user_state import LoggedUserState, UserState


class StepAnswer(TgAnswerInterface):
    """Роутинг ответа по состоянию пользователя."""

    def __init__(self, step: str, answer: TgAnswerInterface, redis: Redis):
        self._step = step
        self._origin = answer
        self._redis = redis

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        step = await LoggedUserState(
            UserState(self._redis, update.chat_id()),
        ).step()
        if step.value != self._step:
            return []
        return await self._origin.build(update)
