import httpx
from aioredis import Redis

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from services.user_state import UserState, UserStep


class ResetStateAnswer(TgAnswerInterface):

    def __init__(self, answer: TgAnswerInterface, redis: Redis):
        self._origin = answer
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        requests = await self._origin.build(update)
        await UserState(
            self._redis, update.chat_id(),
        ).change_step(UserStep.nothing)
        return requests
