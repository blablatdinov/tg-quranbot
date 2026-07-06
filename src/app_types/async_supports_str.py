# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class AsyncSupportsStr(Protocol):
    """Интерфейс объектов, которые можно привести к строке."""

    async def to_str(self) -> str:
        """Приведение к строке."""
