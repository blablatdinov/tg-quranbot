# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from app_types.update import Update


class UpdatesIterator(Protocol):
    """Интерфейс итератора по обновлениям."""

    def __aiter__(self) -> UpdatesIterator:
        """Точка входа в итератор."""

    async def __anext__(self) -> list[Update]:
        """Вернуть следующий элемент."""
