# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.cached_async_int import CachedAsyncInt
from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.tg_chat_id import TgChatId
from srv.podcasts.markupped_podcast_answer import MarkuppedPodcastAnswer
from srv.podcasts.pg_podcast import PgPodcast
from srv.podcasts.podcast_answer import PodcastAnswer
from srv.podcasts.podcast_id import PodcastId


@final
@attrs.define(frozen=True)
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
            CachedAsyncInt(
                PodcastId(self._pgsql, TgChatId(update)),
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
