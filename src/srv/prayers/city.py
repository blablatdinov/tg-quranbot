# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid
from typing import Protocol


class City(Protocol):
    """Интерфейс города."""

    async def city_id(self) -> uuid.UUID:
        """Идентификатор города."""

    async def name(self) -> str:
        """Имя города."""
