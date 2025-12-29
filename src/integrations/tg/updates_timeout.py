# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, final, override

import attrs


@final
@attrs.define(frozen=True)
class UpdatesTimeout(SupportsInt):
    """Таймаут для обновлений."""

    @override
    def __int__(self) -> int:
        """Числовое представление.

        :return: int
        """
        return 5
