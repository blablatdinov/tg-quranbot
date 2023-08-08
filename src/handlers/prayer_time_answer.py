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

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerToSender, TgMessageAnswer, TgTextAnswer
from repository.prayer_time import NewUserPrayers, SafeNotFoundPrayers, SafeUserPrayers, UserPrayers
from services.prayers.invite_set_city_answer import InviteSetCityAnswer, UserWithoutCitySafeAnswer
from services.prayers.prayer_for_user_answer import PrayerForUserAnswer
from services.reset_state_answer import ResetStateAnswer


@final
@attrs.define(frozen=True)
@elegant
class PrayerTimeAnswer(TgAnswerInterface):
    """Ответ с временами намаза."""

    _database: Database
    _redis: Redis
    _empty_answer: TgAnswerInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(self._empty_answer))
        return await UserWithoutCitySafeAnswer(
            ResetStateAnswer(
                PrayerForUserAnswer(
                    answer_to_sender,
                    SafeNotFoundPrayers(
                        self._database,
                        SafeUserPrayers(
                            UserPrayers(self._database),
                            NewUserPrayers(
                                self._database,
                                UserPrayers(self._database),
                            ),
                        ),
                    ),
                ),
                self._redis,
            ),
            InviteSetCityAnswer(
                TgTextAnswer(
                    answer_to_sender,
                    'Вы не указали город, отправьте местоположение или воспользуйтесь поиском',
                ),
                self._redis,
            ),
        ).build(update)
