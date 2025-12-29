# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from app_types.async_supports_str import AsyncSupportsStr


class AdminMessage(AsyncSupportsStr, Protocol):
    """Интерфейс административного сообщения."""

    async def to_str(self) -> str:
        """Чтение содержимого административного сообщения."""
