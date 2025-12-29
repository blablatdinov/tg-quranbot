# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from app_types.intable import AsyncInt


class ValidChatId(AsyncInt, Protocol):
    """Проверенный идентификатор чата."""

    async def to_int(self) -> int:
        """Числовое представление."""
