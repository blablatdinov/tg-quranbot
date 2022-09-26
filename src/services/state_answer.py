import httpx
from aioredis import Redis

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from services.user_state import UserState, LoggedUserState


class StepAnswer(TgAnswerInterface):

    def __init__(self, step: str, answer: TgAnswerInterface, redis: Redis):
        self._step = step
        self._origin = answer
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        step = await LoggedUserState(
            UserState(self._redis, update.chat_id()),
        ).step()
        if not step.value == self._step:
            return []
        return await self._origin.build(update)
