# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class TextSearchQuery(Protocol):
    """Интерфейс запроса для поиска аятов."""

    async def write(self, query: str) -> None:
        """Запись.

        :param query: str
        """

    async def read(self) -> str:
        """Чтение."""
