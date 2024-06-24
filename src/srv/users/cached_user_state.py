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

from typing import final, override

from pyeo import elegant

from srv.users.user_state import UserState
from srv.users.user_step import UserStep


@final
@elegant
class CachedUserState(UserState):
    """Кэширующий декоратор."""

    @override
    def __init__(self, origin: UserState) -> None:
        """Ctor.

        :param origin: UserState
        """
        self._origin = origin
        self._cache: UserStep | None = None

    @override
    async def step(self) -> UserStep:
        """Состояние пользователя.

        :return: UserStep
        """
        if self._cache:
            return self._cache
        self._cache = await self._origin.step()
        return self._cache

    @override
    async def change_step(self, step: UserStep) -> None:
        """Изменение, состояние пользователя.

        :param step: UserStep
        """
        await self._origin.change_step(step)
        self._cache = step
