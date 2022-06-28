from contextlib import asynccontextmanager

import asyncpg

from settings import settings


@asynccontextmanager
async def db_connection():
    """Контекстный менеджер для коннектов к БД.

    :yields: connection
    """
    connection = await asyncpg.connect(settings.DATABASE_URL)
    try:
        yield connection
    finally:
        await connection.close()
