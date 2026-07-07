# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from frozendict import frozendict


class NeighborAyatsButtons(Protocol):
    """Кнопки для клавиатуры с соседними аятами."""

    async def left(self) -> frozendict[str, str] | None:
        """Левая кнопка."""

    async def right(self) -> frozendict[str, str] | None:
        """Правая кнопка."""
