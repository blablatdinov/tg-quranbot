# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_async_int import FkAsyncInt
from exceptions.internal_exceptions import UserNotFoundError
from srv.users.pg_user import PgUser


@pytest.fixture
def legacy_id():
    return 18


@pytest.fixture
def chat_id():
    return 1


@pytest.fixture
def day():
    return 12


@pytest.fixture
async def db_user(chat_id, day, legacy_id, user_factory):
    return await user_factory(chat_id, day=day, legacy_id=legacy_id)


async def test_user(db_user, day, chat_id):
    assert await db_user.day() == day
    assert await db_user.chat_id() == chat_id
    assert await db_user.is_active()


@pytest.mark.usefixtures('db_user')
async def test_legacy_id_ctor(pgsql, legacy_id):
    user = PgUser.legacy_id_ctor(
        FkAsyncInt(legacy_id),
        pgsql,
    )

    assert await user.chat_id() == 1


@pytest.mark.usefixtures('db_user')
async def test_not_found(pgsql):
    user = PgUser.int_ctor(9843, pgsql)

    with pytest.raises(UserNotFoundError):
        await user.day()
    with pytest.raises(UserNotFoundError):
        await user.is_active()
