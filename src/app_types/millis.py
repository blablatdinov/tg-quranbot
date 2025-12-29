# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsFloat, final, override

import attrs


@final
@attrs.define(frozen=True)
class Millis(SupportsFloat):
    """Миллисекунды."""

    _millis: float

    @classmethod
    def seconds_ctor(cls, seconds: float) -> SupportsFloat:
        """Конструктор для секунд.

        :param seconds: float
        :return: Millis
        """
        return Millis(seconds * 1000)  # noqa: PEO102

    @override
    def __float__(self) -> float:
        """Представление в форме числа с плавающей запятой.

        :return: float
        """
        return self._millis
