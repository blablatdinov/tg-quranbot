# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class Counter(Protocol):
    """Протокол счетчика.

    Является интерфейсом для prometheus метрик
    """

    def inc(self) -> None:
        """Увеличение значения счетчика."""
