# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.intable import AsyncIntable, CachedAsyncIntable
from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.chat_id import ChatId, TgChatId
from integrations.tg.tg_answers.interface import TgAnswer
from srv.podcasts.podcast import PgPodcast
from srv.podcasts.podcast_answer import MarkuppedPodcastAnswer, PodcastAnswer


@final
@attrs.define(frozen=True, slots=True)
@elegant
class _PodcastId(AsyncIntable):

    _pgsql: Database
    _chat_id: ChatId

    @override
    async def to_int(self) -> int:
        query = '\n'.join([
            'SELECT p.podcast_id',
            'FROM podcasts AS p',
            'LEFT JOIN podcast_reactions AS pr ON pr.podcast_id = p.podcast_id',
            'WHERE p.podcast_id NOT IN (',
            '    SELECT podcast_id',
            '    FROM podcast_reactions ',
            '    WHERE user_id = :chat_id',
            ')',
            'ORDER BY RANDOM()',
        ])
        podcast_id = await self._pgsql.fetch_val(query, {'chat_id': int(self._chat_id)})
        if not podcast_id:
            return await self._pgsql.fetch_val('SELECT podcast_id FROM podcasts ORDER BY RANDOM()')
        await self._pgsql.execute(
            'INSERT INTO podcast_reactions (podcast_id, user_id, reaction) VALUES (:podcast_id, :user_id, :reaction)',
            {'podcast_id': podcast_id, 'user_id': int(self._chat_id), 'reaction': 'showed'},
        )
        return podcast_id


@final
@attrs.define(frozen=True, slots=True)
@elegant
class RandomPodcastAnswer(TgAnswer):
    """Ответ с подкастом."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        podcast = PgPodcast(
            CachedAsyncIntable(
                _PodcastId(self._pgsql, TgChatId(update)),
            ),
            self._pgsql,
        )
        return await PodcastAnswer(
            self._empty_answer,
            MarkuppedPodcastAnswer(
                self._debug_mode,
                self._empty_answer,
                self._redis,
                self._pgsql,
                podcast,
            ),
            self._redis,
            podcast,
            self._logger,
            show_podcast_id=True,
        ).build(update)
