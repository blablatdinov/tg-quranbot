# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, final, override

import attrs

from app_types.intable import AsyncInt


@final
@attrs.define(frozen=True)
class FkAsyncInt(AsyncInt):
    """Фейковое число."""

    _source: SupportsInt

    @override
    async def to_int(self) -> int:
        """Приведение к числу с возможностью переключения контекста.

        :return: int
        """
        return int(self._source)
