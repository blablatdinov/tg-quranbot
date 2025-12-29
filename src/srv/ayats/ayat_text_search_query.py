# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from redis.asyncio import Redis

from app_types.logger import LogSink
from exceptions.content_exceptions import UserHasNotSearchQueryError
from integrations.tg.fk_chat_id import ChatId
from srv.ayats.text_search_query import TextSearchQuery


@final
@attrs.define(frozen=True)
class AyatTextSearchQuery(TextSearchQuery):
    """Запрос поиска аята."""

    _redis: Redis
    _chat_id: ChatId
    _logger: LogSink

    _key_template = '{0}:ayat_search_query'

    @override
    async def write(self, query: str) -> None:
        """Запись.

        :param query: str
        """
        key = self._key_template.format(int(self._chat_id))
        self._logger.info('Try writing key: {0}, value: {1}'.format(key, query))
        await self._redis.set(key, query)
        self._logger.info('Key: {0} wrote'.format(
            self._key_template.format(int(self._chat_id)),
        ))

    @override
    async def read(self) -> str:
        """Чтение.

        :return: str
        :raises UserHasNotSearchQueryError: user has not search query
        """
        key = self._key_template.format(int(self._chat_id))
        self._logger.info('Try read {0}'.format(key))
        redis_value = await self._redis.get(key)
        if not redis_value:
            msg = "User hasn't search query"
            self._logger.error(msg)
            raise UserHasNotSearchQueryError(msg)
        search_query = redis_value.decode('utf-8')
        self._logger.info('Read value: {0}'.format(search_query))
        return search_query
