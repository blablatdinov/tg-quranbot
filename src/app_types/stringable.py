# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol, override


class SupportsStr(Protocol):
    """Интерфейс объектов, которые можно привести к строке."""

    @override
    def __str__(self) -> str:
        """Приведение к строке."""
