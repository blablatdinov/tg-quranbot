# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class Coordinates(Protocol):
    """Интерфейс координат."""

    def latitude(self) -> float:
        """Ширина."""

    def longitude(self) -> float:
        """Долгота."""
