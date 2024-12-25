# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import datetime
from typing import final, override

import attrs
from databases import Database

from app_types.update import Update
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayer_status import PrayerStatus


@final
@attrs.define(frozen=True)
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
