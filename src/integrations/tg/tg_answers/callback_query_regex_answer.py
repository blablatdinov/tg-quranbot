# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import re
from typing import final, override

import attrs
import httpx

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.exceptions.update_parse_exceptions import CallbackQueryNotFoundError
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgCallbackQueryRegexAnswer(TgAnswer):
    """Маршрутизация ответов по регулярному выражению."""

    _pattern: str
    _answer: TgAnswer
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            callback_query = str(CallbackQueryData(update))
        except CallbackQueryNotFoundError:
            self._logger.debug('Fail on parse callback query data')
            return []
        self._logger.debug('Try match callback query pattern: "{0}", query data: "{1}"'.format(
            self._pattern, callback_query,
        ))
        regex_result = re.search(self._pattern, callback_query)
        if not regex_result:
            self._logger.debug('Callback query regex not matched')
            return []
        self._logger.debug('Callback query regex matched. Regex result: {0}'.format(regex_result))
        return await self._answer.build(update)
