# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import asyncio
from typing import final, override

import attrs

from app_types.runable import Runable
from app_types.sync_runable import SyncRunable


@final
@attrs.define(frozen=True)
class CliApp(SyncRunable):
    """CLI приложение."""

    _origin: Runable

    @override
    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        :return: int
        """
        try:
            asyncio.run(self._origin.run())
        except KeyboardInterrupt:
            return 0
        return 0
