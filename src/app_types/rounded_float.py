# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsFloat, final, override

import attrs


@final
@attrs.define(frozen=True)
class RoundedFloat(SupportsFloat):
    """Округленное дробное число."""

    _origin: SupportsFloat
    _shift_comma: int

    @override
    def __float__(self) -> float:
        """Представление в форме числа с плавающей запятой.

        :return: float
        """
        return round(float(self._origin), self._shift_comma)
