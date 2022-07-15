import asyncpg

from settings import settings


class DBConnection(object):
    """Контексный менеджер для подключения к БД."""

    async def __aenter__(self) -> asyncpg.Connection:
        self._connection = await asyncpg.connect(settings.DATABASE_URL)
        return self._connection

    async def __aexit__(self, *args) -> None:
        await self._connection.close()
