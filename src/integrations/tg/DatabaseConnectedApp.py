from typing import final, override

import attrs

from app_types.runable import Runable


@final
@attrs.define(frozen=True)
@elegant
class DatabaseConnectedApp(Runable):
    """Декоратор для подключения к БД."""

    _pgsql: Database
    _app: Runable

    @override
    async def run(self) -> None:
        """Запуск."""
        await self._pgsql.connect()
        await self._app.run()
