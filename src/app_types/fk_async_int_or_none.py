# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.async_int_or_none import AsyncIntOrNone


@final
@attrs.define(frozen=True)
class FkAsyncIntOrNone(AsyncIntOrNone):
    """FkAsyncIntOrNone."""

    _origin_value: int | None

    @override
    async def to_int(self) -> int | None:
        """Числовое представление.

        :return: int | None
        """
        return self._origin_value
