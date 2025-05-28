# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

from typing import final, override

import pytest

from srv.users.cached_user_state import CachedUserState
from srv.users.user_state import UserState
from srv.users.user_step import UserStep


@final
class SeUserState(UserState):

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
