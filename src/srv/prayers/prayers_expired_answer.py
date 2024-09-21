# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from collections.abc import Sequence
from typing import final, override

import attrs
import httpx

from app_types.update import Update
from exceptions.prayer_exceptions import PrayersNotFoundError
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerList,
    TgAnswerToSender,
    TgChatIdAnswer,
    TgMessageAnswer,
    TgTextAnswer,
)


@final
@attrs.define(frozen=True)
class PrayersExpiredAnswer(TgAnswer):
    """Декоратор для обработки случаев с отсутствием времени намаза на эту дату."""

    _origin: TgAnswer
    _empty_answer: TgAnswer
    _admin_chat_ids: Sequence[int]

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except PrayersNotFoundError as err:
            return await TgAnswerList(
                TgTextAnswer.str_ctor(
                    TgAnswerToSender(TgMessageAnswer(self._empty_answer)),
                    'Время намаза на {0} для города {1} не найдено'.format(
                        err.date.strftime('%d.%m.%Y'), err.city_name or '',
                    ),
                ),
                TgTextAnswer.str_ctor(
                    TgChatIdAnswer(
                        TgMessageAnswer(self._empty_answer),
                        self._admin_chat_ids[0],
                    ),
                    'Время намаза на {0} для города {1} не найдено'.format(
                        err.date.strftime('%d.%m.%Y'), err.city_name or '',
                    ),
                ),
            ).build(update)
