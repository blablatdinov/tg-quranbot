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
from typing import final

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from integrations.nominatim import NominatimCityName
from integrations.tg.coordinates import TgMessageCoordinates
from integrations.tg.tg_answers import TgAnswerFork, TgAnswerToSender, TgMessageAnswer, TgMessageRegexAnswer
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.tg_answers.location_answer import TgLocationAnswer
from integrations.tg.tg_answers.skip_not_processable import TgSkipNotProcessable
from repository.users.user import UserRepository
from services.city.change_city_answer import ChangeCityAnswer, CityNotSupportedAnswer
from services.city.search import SearchCityByCoordinates, SearchCityByName


@final
@attrs.define(frozen=True)
@elegant
class SearchCityAnswer(TgAnswer):
    """Ответ с изменением статуса прочитанности намаза."""

    _database: Database
    _empty_answer: TgAnswer
    _debug: bool
    _redis: Redis

    async def build(self, update) -> list[httpx.Request]:
        """Обработка запроса.

        :param update: Update
        :return: list[httpx.Request]
        """
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(self._empty_answer))
        return await TgSkipNotProcessable(
            TgAnswerFork(
                TgMessageRegexAnswer(
                    '.+',
                    CityNotSupportedAnswer(
                        ChangeCityAnswer(
                            answer_to_sender,
                            SearchCityByName(self._database),
                            self._redis,
                            UserRepository(self._database),
                        ),
                        answer_to_sender,
                    ),
                ),
                TgLocationAnswer(
                    CityNotSupportedAnswer(
                        ChangeCityAnswer(
                            answer_to_sender,
                            SearchCityByCoordinates(
                                SearchCityByName(self._database),
                                NominatimCityName(TgMessageCoordinates(update)),
                            ),
                            self._redis,
                            UserRepository(self._database),
                        ),
                        answer_to_sender,
                    ),
                ),
            ),
        ).build(update)
