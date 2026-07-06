# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import asyncio
from typing import final, override

import attrs

from app_types.sync_runable import SyncRunable
from srv.events.event_hook import EventHook


@final
@attrs.define(frozen=True)
class EventHookApp(SyncRunable):
    """Запускаемый объект."""

    _event_hook: EventHook

    @override
    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        :return: int
        """
        asyncio.run(self._event_hook.catch())
        return 0
