from typing import Protocol

from aioredis import Redis
from loguru import logger


class AyatTextSearchQueryInterface(Protocol):
    """Интерфейс запроса для поиска аятов."""

    async def write(self) -> None:
        """Запись."""

    async def read(self) -> str:
        """Чтение."""


class AyatTextSearchQuery(AyatTextSearchQueryInterface):
    """Запрос поиска аята."""

    _key_template = '{0}:ayat_search_query'

    def __init__(self, redis: Redis, chat_id: int, query: tuple[str, ...] = ()):
        self._redis = redis
        self._query = query
        self._chat_id = chat_id

    @classmethod
    def for_write_cs(cls, redis: Redis, query: str, chat_id: int):
        """Конструктор для записи.

        :param redis: Redis
        :param query: str
        :param chat_id: int
        :return: AyatTextSearchQuery
        """
        return AyatTextSearchQuery(redis, query=(query,), chat_id=chat_id)

    @classmethod
    def for_reading_cs(cls, redis: Redis, chat_id: int):
        """Конструктор для чтения.

        :param redis: Redis
        :param chat_id: int
        :return: AyatTextSearchQuery
        """
        return AyatTextSearchQuery(redis, chat_id=chat_id)

    async def write(self) -> None:
        """Запись.

        :raises ValueError: if query not give
        """
        key = self._key_template.format(self._chat_id)
        logger.info('Try writing key: {0}, value: {1}'.format(key, self._query[0]))
        try:
            await self._redis.set(key, self._query[0])
        except IndexError as err:
            logger.error('Writing {0} fail query not give'.format(key))
            raise ValueError('Query not give') from err
        logger.info('Key: {0} wrote'.format(self._key_template.format(self._chat_id)))

    async def read(self) -> str:
        """Чтение.

        :return: str
        :raises ValueError: user has not search query
        """
        key = self._key_template.format(self._chat_id)
        logger.info('Try read {0}'.format(key))
        redis_value = await self._redis.get(key)
        if not redis_value:
            logger.error("User hasn't search query")
            raise ValueError("User hasn't search query")
        seqrch_query = redis_value.decode('utf-8')
        logger.info('Read value: {0}'.format(seqrch_query))
        return seqrch_query
