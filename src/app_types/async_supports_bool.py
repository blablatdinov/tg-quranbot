# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class AsyncSupportsBool(Protocol):
    """Интерфейс объектов, которые можно привести к булевому значению."""

    async def to_bool(self) -> bool:
        """Приведение к булевому значению."""
