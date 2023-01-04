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
import re

import httpx

from app_types.stringable import Stringable
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgCallbackQueryRegexAnswer(TgAnswerInterface):
    """Маршрутизация ответов по регулярному выражению."""

    def __init__(self, pattern: str, answer: TgAnswerInterface):
        """Конструктор класса.

        :param pattern: str
        :param answer: TgAnswerInterface
        """
        self._pattern = pattern
        self._answer = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            regex_result = re.search(self._pattern, str(CallbackQueryData(update)))
        except AttributeError:
            return []
        if not regex_result:
            return []
        return await self._answer.build(update)
