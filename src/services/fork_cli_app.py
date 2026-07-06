# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Iterable
from typing import final, override

import attrs

from app_types.sync_runable import SyncRunable


@final
@attrs.define(frozen=True)
class ForkCliApp(SyncRunable):
    """Маршрутизация для CLI приложения."""

    _apps: Iterable[SyncRunable]

    @classmethod
    def ctor(cls, *apps: SyncRunable) -> SyncRunable:
        """Конструктор класса.

        :param apps: SyncRunable
        :return: SyncRunable
        """
        return cls(apps)

    @override
    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        :return: int
        """
        for app in self._apps:
            app.run(args)
        return 0
