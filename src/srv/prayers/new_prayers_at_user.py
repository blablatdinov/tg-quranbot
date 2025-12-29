# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import Protocol


class NewPrayersAtUser(Protocol):
    """Новые записи намаза."""

    async def create(self, date: datetime.date) -> None:
        """Создать.

        :param date: datetime.date
        """
