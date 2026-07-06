# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class NeighborAyatsButtons(Protocol):
    """Кнопки для клавиатуры с соседними аятами."""

    async def left(self) -> dict[str, str] | None:
        """Левая кнопка."""

    async def right(self) -> dict[str, str] | None:
        """Правая кнопка."""
