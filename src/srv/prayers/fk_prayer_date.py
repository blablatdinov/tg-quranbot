# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs

from app_types.update import Update
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
class FkPrayerDate(PrayerDate):
    """Фейковая дата времен намаза."""

    _origin: datetime.date

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        :return: datetime.date
        """
        return self._origin
