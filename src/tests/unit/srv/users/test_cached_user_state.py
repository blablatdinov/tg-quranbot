# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import pytest

from app_types.fk_log_sink import FkLogSink
from srv.users.cached_user_state import CachedUserState
from srv.users.redis_user_state import RedisUserState
from srv.users.user_state import UserState
from srv.users.user_step import UserStep


@final
class SeUserState(UserState):  # noqa: PEO200. Fake object for test

    def __init__(self, step: UserStep):
        self._cnt = 0
        self._step = step

    @override
    async def step(self) -> UserStep:
        if self._cnt == 0:
            self._cnt += 1
            return self._step
        raise AssertionError

    @override
    async def change_step(self, step: UserStep) -> None:
        raise NotImplementedError


async def test_without_cd():
    user_state = SeUserState(UserStep.city_search)
    await user_state.step()
    with pytest.raises(AssertionError):
        await user_state.step()


async def test():
    cd_user_state = CachedUserState(SeUserState(UserStep.city_search))

    await cd_user_state.step()
    assert await cd_user_state.step() == UserStep.city_search


async def test_read_cached(fake_redis):
    user_state = CachedUserState(RedisUserState(fake_redis, 1, FkLogSink()))
    await fake_redis.set('1:step', b'city_search')

    assert await user_state.step() == UserStep.city_search
    await fake_redis.set('1:step', b'new value')
    assert await user_state.step() == UserStep.city_search


async def test_write_cached(fake_redis):
    await fake_redis.set('1:step', b'city_search')
    user_state = CachedUserState(RedisUserState(fake_redis, 1, FkLogSink()))
    await user_state.change_step(UserStep.ayat_search)

    assert await user_state.step() == UserStep.ayat_search
