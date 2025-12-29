# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.counter import Counter
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.update import Update


@final
@attrs.define(frozen=True)
class MeasuredAnswer(TgAnswer):
    """Декоратор для экспорта метрик в grafana."""

    _origin: TgAnswer
    _counter: Counter

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        self._counter.inc()
        return await self._origin.build(update)
