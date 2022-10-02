import httpx
from aioredis import Redis

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from services.ayats.ayat_text_search_query import AyatTextSearchQuery


class HighlightedSearchAnswer(TgAnswerInterface):
    """Ответ с подсвеченным поисковым текстом."""

    def __init__(self, answer: TgAnswerInterface, redis: Redis):
        self._origin = answer
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        new_requests = []
        search_query = await AyatTextSearchQuery.for_reading_cs(self._redis, update.chat_id()).read()
        requests = await self._origin.build(update)
        for request in requests:
            text = request.url.params['text']
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
