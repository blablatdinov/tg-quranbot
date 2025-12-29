# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgMessageRegexAnswer
from integrations.tg.tg_chat_id import TgChatId
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.cached_ayat_search_query import CachedAyatSearchQueryAnswer
from srv.ayats.highlighted_search_answer import HighlightedSearchAnswer
from srv.ayats.search_ayat_by_text import SearchAyatByTextAnswer


@final
@attrs.define(frozen=True)
class SearchAyatByKeywordAnswer(TgAnswer):
    """Ответ с временами намаза."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await TgMessageRegexAnswer(
            '.+',
            HighlightedSearchAnswer(
                CachedAyatSearchQueryAnswer(
                    SearchAyatByTextAnswer(
                        self._debug_mode,
                        self._empty_answer,
                        self._redis,
                        self._pgsql,
                        self._logger,
                    ),
                    self._redis,
                    self._logger,
                ),
                AyatTextSearchQuery(
                    self._redis,
                    TgChatId(update),
                    self._logger,
                ),
            ),
        ).build(update)
