# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers.fk_answer import FkAnswer
from services.answers.change_state_answer import ChangeStateAnswer
from srv.users.redis_user_state import RedisUserState
from srv.users.user_step import UserStep


@pytest.fixture
async def state(fake_redis):
    await RedisUserState(
        fake_redis, 534, FkLogSink(),
    ).change_step(UserStep.city_search)


@pytest.mark.usefixtures('state')
async def test(fake_redis, message_update_factory):
    got = await ChangeStateAnswer(
        FkAnswer(),
        fake_redis,
        UserStep.nothing,
        FkLogSink(),
    ).build(FkUpdate(message_update_factory('', 534)))

    assert got[0].url == 'https://some.domain'
    assert (await fake_redis.get('534:step')).decode('utf-8') == UserStep.nothing.value
