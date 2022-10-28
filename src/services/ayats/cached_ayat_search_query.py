import httpx
from aioredis import Redis

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from services.ayats.ayat_text_search_query import AyatTextSearchQuery


class CachedAyatSearchQueryAnswer(TgAnswerInterface):
    """Закешированный запрос пользователя на поиск аятов.

    TODO: что делать если данные из кэша будут удалены
    """

    def __init__(self, answer: TgAnswerInterface, redis: Redis):
        self._origin = answer
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        await AyatTextSearchQuery.for_write_cs(
            self._redis,
            update.message().text(),
            update.chat_id(),
        ).write()
        return await self._origin.build(update)
