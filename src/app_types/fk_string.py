# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.stringable import SupportsStr


@final
@attrs.define(frozen=True)
class FkString(SupportsStr):
    """Обертка для строки."""

    _source: str

    @override
    def __str__(self) -> str:
        """Строковое представление.

        :return: str
        """
        return self._source
