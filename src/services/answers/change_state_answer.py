import httpx
from redis.asyncio import Redis

from app_types.stringable import Stringable
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface
from services.user_state import LoggedUserState, UserState, UserStep


class ChangeStateAnswer(TgAnswerInterface):
    """Ответ, с изменением шага пользователя."""

    def __init__(self, answer: TgAnswerInterface, redis: Redis, step: UserStep):
        self._origin = answer
        self._step = step
        self._redis = redis

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        await LoggedUserState(
            UserState(self._redis, int(TgChatId(update))),
        ).change_step(self._step)
        return await self._origin.build(update)
