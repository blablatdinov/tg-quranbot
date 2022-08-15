import pytest
from databases import Database

from settings import settings


@pytest.fixture()
async def db_session():
    session = Database(settings.TEST_DATABASE_URL, force_rollback=True)
    await session.connect()
    yield session
    await session.disconnect()
