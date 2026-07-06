# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class NewUser(Protocol):
    """Новый пользователь."""

    async def create(self) -> None:
        """Создание."""
