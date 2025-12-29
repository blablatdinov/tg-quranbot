# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from srv.ayats.text_search_query import TextSearchQuery


@final
@attrs.define(frozen=True)
class HighlightedSearchAnswer(TgAnswer):
    """Ответ с подсвеченным поисковым текстом."""

    _origin: TgAnswer
    _search_query: TextSearchQuery

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        new_requests = []
        requests = await self._origin.build(update)
        search_query = await self._search_query.read()
        for request in requests:
            text = request.url.params.get('text')
            if not text:
                new_requests.append(request)
                continue
            if search_query in text:
                new_requests.append(httpx.Request(
                    method=request.method,
                    url=request.url.copy_set_param(
                        'text',
                        request.url.params['text'].replace(search_query, '<b>{0}</b>'.format(search_query)),
                    ),
                    headers=request.headers,
                ))
            else:
                new_requests.append(request)
        return new_requests
