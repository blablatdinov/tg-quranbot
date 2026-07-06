# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class User(Protocol):
    """Интерфейс пользователя."""

    async def chat_id(self) -> int:
        """Идентификатор чата."""

    async def day(self) -> int:
        """День для рассылки утреннего контента."""

    async def is_active(self) -> bool:
        """Статус активности пользователя."""
