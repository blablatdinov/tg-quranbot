# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class UpdatedUserCity(Protocol):
    """Обновленный город у пользователя."""

    async def update(self) -> None:
        """Обновление."""
