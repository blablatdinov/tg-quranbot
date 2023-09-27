import pytest

from srv.users.pg_user import PgUser


@pytest.fixture()
async def user_id(pgsql):
    await pgsql.execute('INSERT INTO users (chat_id, day) VALUES (1, 12)')
    return 1


async def test_day(user_id, pgsql):
    assert await PgUser.int_ctor(user_id, pgsql).day() == 12
