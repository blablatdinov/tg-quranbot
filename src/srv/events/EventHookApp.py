from app_types.sync_runable import SyncRunable
from srv.events.event_hook import EventHook


import attrs
from pyeo import elegant


import asyncio
from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
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