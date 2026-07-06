# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class EventHook(Protocol):
    """Обработчик событий из очереди."""

    async def catch(self) -> None:
        """Запуск обработки."""
