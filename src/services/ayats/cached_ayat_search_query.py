import httpx
from aioredis import Redis

from app_types.stringable import Stringable
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswerInterface
from services.ayats.ayat_text_search_query import AyatTextSearchQuery


class CachedAyatSearchQueryAnswer(TgAnswerInterface):
    """Закешированный запрос пользователя на поиск аятов.

    TODO: что делать если данные из кэша будут удалены
    """

    def __init__(self, answer: TgAnswerInterface, redis: Redis):
        self._origin = answer
        self._redis = redis

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        await AyatTextSearchQuery.for_write_cs(
            self._redis,
            str(MessageText(update)),
            int(TgChatId(update)),
        ).write()
        return await self._origin.build(update)
