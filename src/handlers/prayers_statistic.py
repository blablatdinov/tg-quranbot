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
from itertools import batched
from typing import final, override

import attrs
from databases import Database
from dateutil import rrule

from app_types.async_supports_str import AsyncSupportsStr
from integrations.tg.fk_chat_id import ChatId
from srv.prayers.new_prayers import NewPrayersAtUser
from srv.prayers.prayer_names import PrayerNames


@final
@attrs.define(frozen=True)
class PrayersStatistic(AsyncSupportsStr):
    """Статистика непрочитанных намазов."""

    _prayers_at_user: NewPrayersAtUser
    _chat_id: ChatId
    _pgsql: Database

    @override
    async def to_str(self) -> str:
        """Приведение к строке.

        :return: str
        """
        idx = 0
        prayer_unread_dict = dict.fromkeys(PrayerNames.names(), 0)
        prayers_per_day = await self._prayers_per_day()
        for date in await self._dates_range():
            if date == prayers_per_day[idx][0]['day']:
                self._exist_prayer_case(prayers_per_day, prayer_unread_dict, idx)
                idx += 1
            else:
                await self._new_prayer_at_user_case(prayer_unread_dict, date)
        return '\n'.join([
            'Кол-во непрочитанных намазов:\n',
            'Иртәнге: {0}'.format(prayer_unread_dict[PrayerNames.fajr.name]),
            'Өйлә: {0}'.format(prayer_unread_dict[PrayerNames.dhuhr.name]),
            'Икенде: {0}'.format(prayer_unread_dict[PrayerNames.asr.name]),
            'Ахшам: {0}'.format(prayer_unread_dict[PrayerNames.maghrib.name]),
            'Ястү: {0}'.format(prayer_unread_dict[PrayerNames.isha.name]),
        ])

    def _exist_prayer_case(  # noqa: NPM100. Fix it
        self,
        prayers_per_day: list[tuple],
        prayer_unread_dict: dict,
        idx: int,
    ) -> None:
        for prayer_idx, prayer_name in enumerate(PrayerNames.names()):
            prayer_unread_dict[prayer_name] += int(not prayers_per_day[idx][prayer_idx]['is_read'])

    async def _new_prayer_at_user_case(  # noqa: NPM100. Fix it
        self,
        prayer_unread_dict: dict,
        date: datetime.date,
    ) -> None:
        await self._prayers_at_user.create(date)
        for prayer_name in PrayerNames.names():
            prayer_unread_dict[prayer_name] += 1

    async def _prayers_per_day(self) -> list[tuple]:  # noqa: NPM100. Fix it
        query = '\n'.join([
            'SELECT',
            '    pau.is_read,',
            '    p.day,',
            '    p.name',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p ON pau.prayer_id = p.prayer_id',
            'WHERE pau.user_id = :chat_id',
            "ORDER BY p.day, ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
        ])
        return list(batched(
            await self._pgsql.fetch_all(query, {
                'chat_id': int(self._chat_id),
            }),
            5,
        ))

    async def _dates_range(self) -> list[datetime.date]:  # noqa: NPM100. Fix it
        query = '\n'.join([
            'SELECT p.day',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p ON pau.prayer_id = p.prayer_id',
            'WHERE pau.user_id = :chat_id',
            "ORDER BY p.day, ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
        ])
        rows = await self._pgsql.fetch_all(query, {'chat_id': int(self._chat_id)})
        if not rows:
            return []
        return [
            dt.date()
            for dt in rrule.rrule(
                rrule.DAILY,
                dtstart=rows[0]['day'],
                until=rows[-1]['day'],
            )
        ]
