# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from srv.users.user_step import UserStep


class UserState(Protocol):
    """Интерфейс для работы с состоянием пользователя."""

    async def step(self) -> UserStep:
        """Состояние пользователя."""

    async def change_step(self, step: UserStep) -> None:
        """Изменение, состояние пользователя.

        :param step: UserStep
        """
