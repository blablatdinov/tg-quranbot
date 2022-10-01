import httpx
from aioredis import Redis

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from services.user_state import LoggedUserState, UserState, UserStep


class ChangeStateAnswer(TgAnswerInterface):
    """Ответ, с изменением шага пользователя."""

    def __init__(self, answer: TgAnswerInterface, redis: Redis, step: UserStep):
        self._origin = answer
        self._step = step
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        await LoggedUserState(
            UserState(self._redis, update.chat_id()),
        ).change_step(self._step)
        return await self._origin.build(update)
