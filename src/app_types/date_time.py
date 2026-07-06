# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime as dt
from typing import Protocol


class DateTime(Protocol):
    """Интерфейс даты/времени."""

    def datetime(self) -> dt.datetime:
        """Дата/время."""
