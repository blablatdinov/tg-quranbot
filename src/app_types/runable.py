# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class Runable(Protocol):
    """Интерфейс запускаемого объекта."""

    async def run(self) -> None:
        """Запуск."""
