# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
from fakeredis import aioredis

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers.fk_answer import FkAnswer
from integrations.tg.update import TgUpdate
from services.reset_state_answer import ResetStateAnswer
from srv.users.redis_user_state import RedisUserState


@pytest.fixture
def fake_redis():
    return aioredis.FakeRedis()


async def test_redis_query(fake_redis):
    await ResetStateAnswer(
        FkAnswer(),
        RedisUserState(fake_redis, 123, FkLogSink()),
    ).build(TgUpdate({'from': {'id': 123}}))

    assert await fake_redis.get('123:step') == b'nothing'


async def test_origin_answer_not_modificated(fake_redis):
    got = await ResetStateAnswer(
        FkAnswer(),
        RedisUserState(fake_redis, 123, FkLogSink()),
    ).build(TgUpdate({'from': {'id': 123}}))
    origin = (await FkAnswer().build(FkUpdate.empty_ctor()))[0].url

    assert got[0].url == origin
