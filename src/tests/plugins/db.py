import asyncio

import pytest
from databases import Database

from settings import settings


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture()
async def db_session(test_db, event_loop):
    session = Database(settings.TEST_DATABASE_URL, force_rollback=True)
    await session.connect()
    yield session
    await session.disconnect()
