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

import httpx
from aioredis import Redis

from app_types.stringable import Stringable
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerMarkup
from services.switch_inline_query_answer import SwitchInlineQueryKeyboard
from services.user_state import LoggedUserState, UserState, UserStep


@final
class UserWithoutCitySafeAnswer(TgAnswerInterface):
    """Объект для обработки случаев когда пользователь запрашивает время намаза без установленного города."""

    def __init__(self, prayer_time_answer: TgAnswerInterface, invite_set_city_answer: TgAnswerInterface):
        """Конструктор класса.

        :param prayer_time_answer: TgAnswerInterface
        :param invite_set_city_answer: TgAnswerInterface
        """
        self._origin = prayer_time_answer
        self._invite_set_city_answer = invite_set_city_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except UserHasNotCityIdError:
            return await self._invite_set_city_answer.build(update)


@final
class InviteSetCityAnswer(TgAnswerInterface):
    """Ответ с приглашением ввести город."""

    def __init__(self, message_answer: TgAnswerInterface, redis: Redis):
        """Конструктор класса.

        :param message_answer: TgAnswerInterface
        :param redis: Redis
        """
        self._message_answer = message_answer
        self._redis = redis

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        await LoggedUserState(
            UserState(self._redis, int(TgChatId(update))),
        ).change_step(UserStep.city_search)
        return await TgAnswerMarkup(
            self._message_answer,
            SwitchInlineQueryKeyboard(),
        ).build(update)
