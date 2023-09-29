"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import final

import attrs
from loguru import logger
from redis.asyncio import Redis

from srv.ayats.text_search_query import TextSearchQuery


@final
@attrs.define
class CachedTextSearchQuery(TextSearchQuery):

    _origin: TextSearchQuery
    _cached: str = ''

    async def write(self, query: str) -> None:
        """Запись.

        :raises ValueError: if query not give
        """
        await self._origin.write(query)
        self._cached = query

    async def read(self) -> str:
        """Чтение.

        :return: str
        """
        if self._cached:
            return self._cached
        self._cached = await self._origin.read()
        return self._cached


@final
@attrs.define(frozen=True)
class AyatTextSearchQuery(TextSearchQuery):
    """Запрос поиска аята."""

    _redis: Redis
    _chat_id: int  # TODO #360/30min переделать тип на ChatId

    _key_template = '{0}:ayat_search_query'

    async def write(self, query: str) -> None:
        """Запись.

        :raises ValueError: if query not give
        """
        key = self._key_template.format(self._chat_id)
        logger.info('Try writing key: {0}, value: {1}'.format(key, query))
        await self._redis.set(key, query)
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
            msg = "User hasn't search query"
            logger.error(msg)
            raise ValueError(msg)
        seqrch_query = redis_value.decode('utf-8')
        logger.info('Read value: {0}'.format(seqrch_query))
        return seqrch_query
