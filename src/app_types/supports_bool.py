# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class SupportsBool(Protocol):
    """Интерфейс объектов, которые можно привести к булевому значению."""

    def __bool__(self) -> bool:
        """Приведение к булевому значению."""
