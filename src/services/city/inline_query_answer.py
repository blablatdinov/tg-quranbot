import json

import httpx

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
