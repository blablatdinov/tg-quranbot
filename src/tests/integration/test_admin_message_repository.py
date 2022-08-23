import pytest

from repository.admin_message import AdminMessageRepository


@pytest.fixture()
async def admin_message(db_session):
    await db_session.execute("INSERT INTO admin_messages (key, text) VALUES ('start_message', 'Hello')")


async def test(db_session, admin_message):
    got = await AdminMessageRepository(db_session).get('start_message')

    assert got == 'Hello'
