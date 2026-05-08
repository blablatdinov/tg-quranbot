# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Iterator
from typing import Self, final, override

import attrs


@final
@attrs.define(frozen=True)
class DefaultBackoff(Iterator[int]):
    """Итератор для задержки между отправкой сообщений."""

    def __init__(self) -> None:
        """Ctor."""
        self._step = 0

    @override
    def __next__(self) -> int:
        """Получить следующий элемент."""
        val = [2, 3, 5][self._step]
        self._step += 1
        return val

    @override
    def __iter__(self) -> Self:
        return self
