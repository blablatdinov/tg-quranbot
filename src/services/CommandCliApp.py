from typing import final, override

import attrs
from pyeo import elegant

from app_types.sync_runable import SyncRunable


@final
@attrs.define(frozen=True)
@elegant
class CommandCliApp(SyncRunable):
    """CLI команда."""

    _command: str
    _app: SyncRunable

    @override
    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        :return: int
        """
        if args[1] != self._command:
            return 1
        self._app.run(args)
        return 0
