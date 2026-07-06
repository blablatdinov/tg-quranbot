# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class AsyncInt(Protocol):
    """Интерфейс объектов, которые можно привести к числу."""

    async def to_int(self) -> int:
        """Приведение к числу с возможностью переключения контекста."""
