# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

from srv.users.user_state import UserState
from srv.users.user_step import UserStep


@final
class CachedUserState(UserState):  # noqa: PEO200. Cached decorator
    """Кэширующий декоратор."""

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
