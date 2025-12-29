# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.async_supports_str import AsyncSupportsStr


@final
@attrs.define(frozen=True)
class FkAsyncStr(AsyncSupportsStr):
    """Обертка для строки."""

    _source: str

    @override
    async def to_str(self) -> str:
        """Строковое представление.

        :return: str
        """
        return self._source
