# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgMessageAnswer, TgTextAnswer
from integrations.tg.tg_answers.answer_to_sender import TgAnswerToSender
from integrations.tg.tg_chat_id import TgChatId
from settings import Settings
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.highlighted_search_answer import HighlightedSearchAnswer
from srv.ayats.search_ayat_by_text_callback_answer import SearchAyatByTextCallbackAnswer
from srv.ayats.user_has_not_search_query_safe_answer import UserHasNotSearchQuerySafeAnswer


@final
@attrs.define(frozen=True)
class PaginateBySearchAyat(TgAnswer):
    """Пагинация по поиску аятов."""

    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database
    _settings: Settings
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await UserHasNotSearchQuerySafeAnswer(
            HighlightedSearchAnswer(
                SearchAyatByTextCallbackAnswer(
                    self._settings.DEBUG,
                    self._empty_answer,
                    self._redis,
                    self._pgsql,
                    self._logger,
                ),
                AyatTextSearchQuery(self._redis, TgChatId(update), self._logger),
            ),
            TgAnswerToSender(
                TgTextAnswer.str_ctor(
                    TgMessageAnswer(self._empty_answer),
                    'Пожалуйста, введите запрос для поиска:',
                ),
            ),
        ).build(update)
