# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class UpdatedUsersStatus(Protocol):
    """Обновление статусов пользователей."""

    async def update(self, to: bool) -> None:
        """Обновление.

        :param to: bool
        """
