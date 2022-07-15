import asyncpg
from asyncpg import Connection

from settings import settings


class DBConnection(object):

    async def __aenter__(self) -> Connection:
        self._connection = await asyncpg.connect(settings.DATABASE_URL)
        return self._connection

    async def __aexit__(self, *args) -> None:
        await self._connection.close()
