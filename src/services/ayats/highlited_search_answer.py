import httpx
from aioredis import Redis

from app_types.stringable import Stringable
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface
from services.ayats.ayat_text_search_query import AyatTextSearchQuery


class HighlightedSearchAnswer(TgAnswerInterface):
    """Ответ с подсвеченным поисковым текстом."""

    def __init__(self, answer: TgAnswerInterface, redis: Redis):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param redis: Redis
        """
        self._origin = answer
        self._redis = redis

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        new_requests = []
        requests = await self._origin.build(update)
        search_query = await AyatTextSearchQuery.for_reading_cs(
            self._redis,
            int(TgChatId(update)),
        ).read()
        for request in requests:
            try:
                text = request.url.params['text']
            except KeyError:
                continue
            if search_query in text:
                new_requests.append(httpx.Request(
                    method=request.method,
                    url=request.url.copy_set_param(
                        'text',
                        text.replace('+', ' ') .replace(search_query, '<b>{0}</b>'.format(search_query)),
                    ),
                    headers=request.headers,
                ))
            else:
                new_requests.append(request)
        return new_requests
