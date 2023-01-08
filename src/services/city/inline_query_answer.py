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
import json

import httpx

from typing import final
from app_types.stringable import Stringable
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.inline_query import InlineQuery, InlineQueryId
from integrations.tg.tg_answers import TgAnswerInterface
from services.city.search import CitySearchInterface, SearchCityQuery
from services.debug_answer import DebugAnswer


class InlineQueryAnswer(TgAnswerInterface):
    """Ответ на инлайн поиск."""

    def __init__(self, answer: TgAnswerInterface, cities: CitySearchInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param cities: CitySearchInterface
        """
        self._origin = answer
        self._cities = cities

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        :raises NotProcessableUpdateError: if update hasn't inline query
        """
        try:
            inline_query_data = str(InlineQuery(update))
        except AttributeError as err:
            raise NotProcessableUpdateError from err
        origin_requests = await DebugAnswer(self._origin).build(update)
        cities = await self._cities.search(
            SearchCityQuery.from_string_cs(inline_query_data),
        )
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
                        json.dumps([
                            {
                                'id': str(idx),
                                'type': 'article',
                                'title': city.name,
                                'input_message_content': {'message_text': city.name},
                            }
                            for idx, city in enumerate(cities)
                        ]),
                    )
                ),
            ),
        ]
