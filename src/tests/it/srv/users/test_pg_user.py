# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import pytest

from app_types.fk_async_int import FkAsyncInt
from srv.users.pg_user import PgUser


@pytest.fixture
def legacy_id():
    return 18


@pytest.fixture
async def user_id(pgsql, legacy_id):
    await pgsql.execute(
        'INSERT INTO users (chat_id, day, legacy_id) VALUES (1, 12, :legacy_id)',
        {'legacy_id': legacy_id},
    )
    return 1


async def test_user(user_id, pgsql):
    user = PgUser.int_ctor(user_id, pgsql)

    assert await user.day() == 12
    assert await user.chat_id() == 1
    assert await user.is_active()


@pytest.mark.usefixtures('user_id')
async def test_legacy_id_ctor(pgsql, legacy_id):
    user = PgUser.legacy_id_ctor(
        FkAsyncInt(legacy_id),
        pgsql,
    )

    assert await user.chat_id() == 1
