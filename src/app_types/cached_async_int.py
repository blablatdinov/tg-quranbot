# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

from app_types.intable import AsyncInt


@final
class CachedAsyncInt(AsyncInt):  # noqa: PEO200. Class has mutable state for caching
    """Кэшируемое число."""

    def __init__(self, origin: AsyncInt) -> None:
        """Конструктор.

        :param origin: AsyncIntable
        """
        self._origin = origin
        self._cached = False
        self._cached_value = 0

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        """
        if self._cached:
            return self._cached_value
        int_val = await self._origin.to_int()
        self._cached = True
        self._cached_value = int_val
        return int_val
