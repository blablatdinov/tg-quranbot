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

import traceback
from collections.abc import Iterable
from typing import final, override

import attrs
import httpx

from app_types.logger import LogSink
from app_types.update import Update
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.exceptions.update_parse_exceptions import (
    CallbackQueryNotFoundError,
    CoordinatesNotFoundError,
    InlineQueryNotFoundError,
    MessageIdNotFoundError,
)
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgAnswerFork(TgAnswer):
    """Маршрутизация ответов."""

    _answers: Iterable[TgAnswer]
    _logger: LogSink

    @classmethod
    def ctor(cls, logger: LogSink, *answers: TgAnswer) -> TgAnswer:
        """Конструктор класса.

        :param answers: TgAnswerInterface
        :param logger: LogSink
        :return: TgAnswer
        """
        return cls(
            answers,
            logger,
        )

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        :raises NotProcessableUpdateError: if not found matches
        """
        exceptions = (
            CoordinatesNotFoundError,
            CallbackQueryNotFoundError,
            MessageIdNotFoundError,
            InlineQueryNotFoundError,
        )
        for answer in self._answers:
            try:
                origin_requests = await answer.build(update)
            except exceptions as err:
                self._logger.debug('Fork iteration error: {0}. Traceback: {1}'.format(str(err), traceback.format_exc()))
                continue
            if origin_requests:
                self._logger.debug('Update processed by: {handler}', handler=answer)
                return origin_requests
        raise NotProcessableUpdateError
