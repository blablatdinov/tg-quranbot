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

from typing import final, override

import attrs
import httpx

from app_types.stringable import SupportsStr
from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True, repr=False)
class TgEmptyAnswer(TgAnswer, SupportsStr):
    """Пустой ответ."""

    _token: str

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Создать ответ с токеном.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [httpx.Request('GET', httpx.URL('https://api.telegram.org/bot{0}/'.format(self._token)))]

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        return 'TgEmptyAnswer(token=...)'
