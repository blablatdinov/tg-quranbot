# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.runable import Runable


@final
@attrs.define(frozen=True)
class DatabaseConnectedApp(Runable):
    """Декоратор для подключения к БД."""

    _pgsql: Database
    _app: Runable

    @override
    async def run(self) -> None:
        """Запуск."""
        await self._pgsql.connect()
        await self._app.run()
