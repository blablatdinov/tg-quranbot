# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import traceback
from typing import final, override

import attrs
import httpx

from app_types.logger import LogSink
from app_types.update import Update
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer


@final
@attrs.define(frozen=True)
class SafeFork(TgAnswer):
    """Безопасный Fork."""

    _origin: TgAnswer
    _message_answer: TgAnswer
    _log: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :returns: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except NotProcessableUpdateError as err:
            self._log.error('Error on process update: {0}. Traceback: {1}'.format(err, traceback.format_exc()))
            return await TgTextAnswer.str_ctor(
                self._message_answer, 'Я не знаю как отвечать на такое сообщение',
            ).build(update)
