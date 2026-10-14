# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import Protocol


class DateTime(Protocol):
    """Интерфейс даты/времени."""

    def date_time(self) -> datetime.datetime:
        """Дата/время."""
