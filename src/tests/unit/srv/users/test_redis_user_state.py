# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
from fakeredis import aioredis

from app_types.fk_log_sink import FkLogSink
from srv.users.redis_user_state import RedisUserState
from srv.users.user_step import UserStep


@pytest.fixture
def fake_redis():
    return aioredis.FakeRedis()


async def test_not_exists_state(fake_redis):
    got = await RedisUserState(fake_redis, 879435, FkLogSink()).step()

    assert got == UserStep.nothing
