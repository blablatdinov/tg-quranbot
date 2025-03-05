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
from app_types.stringable import SupportsStr

import attrs
import httpx
import pytz
from databases import Database
from lxml import etree

from app_types.fk_update import FkUpdate
from exceptions.prayer_exceptions import PrayersNotFoundError
from srv.prayers.city import City
from srv.prayers.dr_prayers_url import DrPrayersUrl
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
@attrs.define(frozen=True)
class _NormalizedTime(SupportsStr):

    _time_str: str

    @override
    def __str__(self):
        hours, minutes = map(int, self._time_str.split(':'))
        return "{0:02}:{1:02}".format(hours, minutes)


@final
@attrs.define(frozen=True)
class DrPrayersInfo(PrayersInfo):
    """Информация о времени намаза с сайта https://dumrt.ru ."""

    _city: City
    _date: PrayerDate
    _pgsql: Database

    @override
    async def to_dict(self) -> PrayerMessageTextDict:  # noqa: WPS210
        """Словарь с данными для отправки пользователю."""
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                await DrPrayersUrl(self._city, self._pgsql).to_str(),
            )
            response.raise_for_status()
        date = await self._date.parse(FkUpdate.empty_ctor())
        for line in response.text.splitlines():
            splitted_line = line.split(';')
            if splitted_line[0] == date.strftime('%Y-%m-%d'):
                break
        from pprint import pprint
        pprint(list(enumerate(splitted_line)))
        return PrayerMessageTextDict({
            'city_name': await self._city.name(),
            'date': date.strftime('%d.%m.%Y'),
            'fajr_prayer_time': str(_NormalizedTime(splitted_line[1])),
            'sunrise_prayer_time': str(_NormalizedTime(splitted_line[3])),
            'dhuhr_prayer_time': str(_NormalizedTime(splitted_line[4])),
            'asr_prayer_time': str(_NormalizedTime(splitted_line[6])),
            'magrib_prayer_time': str(_NormalizedTime(splitted_line[7])),
            'ishaa_prayer_time': str(_NormalizedTime(splitted_line[8])),
        })
