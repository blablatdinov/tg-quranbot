from app_types.update import Update
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayer_status import PrayerStatus


import attrs
from databases import Database
from pyeo import elegant


import datetime
from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class DateFromUserPrayerId(PrayerDate):
    """Дата намаза по идентификатору времени намаза."""

    _pgsql: Database

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из идентификатора времени намаза.

        :param update: Update
        :return: datetime.date
        """
        query = '\n'.join([
            'SELECT prayers.day',
            'FROM prayers_at_user',
            'INNER JOIN prayers ON prayers_at_user.prayer_id = prayers.prayer_id',
            'WHERE prayer_at_user_id = :prayer_at_user_id',
        ])
        return await self._pgsql.fetch_val(query, {
            'prayer_at_user_id': PrayerStatus.update_ctor(update).user_prayer_id(),
        })