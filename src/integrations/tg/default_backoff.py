# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Iterator
from typing import Self, final, override

import attrs


@final
@attrs.define()
class DefaultBackoff(Iterator[int]):
    """Итератор для задержки между отправкой сообщений."""

    _step: int = 0

    @override
    def __next__(self) -> int:
        """Получить следующий элемент."""
        arr = [2, 3, 5]
        if self._step >= len(arr):
            raise StopIteration
        val = arr[self._step]
        self._step += 1
        return val

    @override
    def __iter__(self) -> Self:
        return self
