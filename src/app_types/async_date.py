# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import Protocol


class AsyncDate(Protocol):
    """Интерфейс даты для вычисления с возможностью переключения контекста."""

    async def date(self) -> datetime.date:
        """Дата."""
