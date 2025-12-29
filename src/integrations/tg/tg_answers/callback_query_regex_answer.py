# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
