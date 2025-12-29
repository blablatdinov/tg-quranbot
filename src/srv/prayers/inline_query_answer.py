# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
import ujson
from databases import Database

from app_types.update import Update
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.exceptions.update_parse_exceptions import InlineQueryNotFoundError
from integrations.tg.inline_query import InlineQuery
from integrations.tg.inline_query_id import InlineQueryId
from integrations.tg.tg_answers import TgAnswer
from services.debug_answer import DebugAnswer
from srv.prayers.pg_city_names import PgCityNames


@final
@attrs.define(frozen=True)
class InlineQueryAnswer(TgAnswer):
    """Ответ на инлайн поиск городов."""

    _origin: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        :raises NotProcessableUpdateError: if update hasn't inline query
        """
        try:
            inline_query_data = str(InlineQuery(update))
        except InlineQueryNotFoundError as err:
            raise NotProcessableUpdateError from err
        origin_requests = await DebugAnswer(self._origin).build(update)
        city_names = await PgCityNames(self._pgsql, inline_query_data).to_list()
        return [
            httpx.Request(
                origin_requests[0].method,
                (
                    origin_requests[0]
                    .url
                    .join('answerInlineQuery')
                    .copy_add_param('inline_query_id', int(InlineQueryId(update)))
                    .copy_add_param(
                        'results',
                        ujson.dumps([
                            {
                                'id': str(idx),
                                'type': 'article',
                                'title': city_name,
                                'input_message_content': {'message_text': city_name},
                            }
                            for idx, city_name in enumerate(city_names)
                        ]),
                    )
                ),
            ),
        ]
