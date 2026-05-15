# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import asyncio
from collections.abc import Iterator
from typing import SupportsInt, cast, final, override

import attrs
import httpx

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.sendable import Sendable


@final
@attrs.define(frozen=True)
class RetriedSendable(Sendable):
    """Переотправка проваленных сообщений."""

    _origin: Sendable
    _logger: LogSink
    _attempts: SupportsInt
    _backoff: Iterator[int]

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка."""
        last_exception = None
        for attempt in range(1, int(self._attempts) + 1):
            try:
                return await self._origin.send(update)
            except httpx.ConnectTimeout as err:
                last_exception = err
                backoff = next(self._backoff)
                self._logger.info('Attempt {0} failed. Wait {1} seconds'.format(attempt, backoff))
                await asyncio.sleep(backoff)
        raise cast('Exception', last_exception)
