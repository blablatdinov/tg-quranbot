# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from srv.ayats.ayat import Ayat


class NeighborAyats(Protocol):
    """Интерфейс для работы с соседними аятами в хранилище."""

    async def left_neighbor(self) -> Ayat:
        """Левый аят."""

    async def right_neighbor(self) -> Ayat:
        """Правый аят."""

    async def page(self) -> str:
        """Информация о странице."""
