# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.update import Update
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayer_status import PrayerStatus


@final
@attrs.define(frozen=True)
class DateFromUserPrayerId(PrayerDate):
    """Дата намаза по идентификатору времени намаза."""

    _pgsql: AsyncEngine

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
        async with self._pgsql.connect() as conn:
            result = await conn.execute(text(query), {
                'prayer_at_user_id': PrayerStatus.update_ctor(update).user_prayer_id(),
            })
            row = result.fetchone()
        if row is None:
            raise ValueError('Prayer not found')
        return row[0]
