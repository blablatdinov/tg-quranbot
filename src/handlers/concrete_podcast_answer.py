# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.fk_async_int import FkAsyncInt
from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers.tg_answer import TgAnswer
from services.intable_regex import IntableRegex
from srv.podcasts.markupped_podcast_answer import MarkuppedPodcastAnswer
from srv.podcasts.pg_podcast import PgPodcast
from srv.podcasts.podcast_answer import PodcastAnswer


@final
@attrs.define(frozen=True)
class ConcretePodcastAnswer(TgAnswer):
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
            FkAsyncInt(IntableRegex(str(MessageText(update)))),
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
            show_podcast_id=False,
        ).build(update)
