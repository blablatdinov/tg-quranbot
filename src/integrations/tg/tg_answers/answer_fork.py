# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
