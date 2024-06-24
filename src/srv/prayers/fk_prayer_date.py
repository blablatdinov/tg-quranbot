import datetime
from typing import final, override

import attrs
from pyeo import elegant

from app_types.update import Update
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
@elegant
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
