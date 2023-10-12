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
from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswer
from settings.debug_mode import DebugMode
from settings.settings import Settings
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.highlighted_search_answer import HighlightedSearchAnswer
from srv.ayats.search_ayat_by_text_callback_answer import SearchAyatByTextCallbackAnswer


@final
@attrs.define(frozen=True)
@elegant
class PaginateBySearchAyat(TgAnswer):
    """Пагинация по поиску аятов."""

    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database
    _settings: Settings

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await HighlightedSearchAnswer(
            SearchAyatByTextCallbackAnswer(
                DebugMode(self._settings), self._empty_answer, self._redis, self._pgsql,
            ),
            AyatTextSearchQuery(self._redis, int(TgChatId(update))),
        ).build(update)
