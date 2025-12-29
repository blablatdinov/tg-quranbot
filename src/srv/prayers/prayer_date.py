# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import Protocol

from app_types.update import Update


class PrayerDate(Protocol):
    """Дата времен намаза."""

    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        """
