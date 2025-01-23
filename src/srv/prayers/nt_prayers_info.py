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
import httpx
import pytz
from databases import Database
from lxml import etree

from app_types.fk_update import FkUpdate
from exceptions.prayer_exceptions import PrayersNotFoundError
from srv.prayers.city import City
from srv.prayers.nt_prayers_url import NtPrayersUrl
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
@attrs.define(frozen=True)
class NtPrayersInfo(PrayersInfo):
    """Информация о времени намаза с сайта https://namaz.today ."""

    _city: City
    _date: PrayerDate
    _pgsql: Database

    # TODO #1501:30min Исправить кол-во переменных и удалить noqa комментарий
    @override
    async def to_dict(self) -> PrayerMessageTextDict:  # noqa: WPS210
        """Словарь с данными для отправки пользователю."""
        city_name = await self._city.name()
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                await NtPrayersUrl(self._city, self._pgsql).to_str(),
            )
            response.raise_for_status()
        tree = etree.fromstring(response.text, etree.HTMLParser())  # noqa: S320. Trust https://namaz.today
        date = await self._date.parse(FkUpdate.empty_ctor())
        if date.month != datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).month:
            raise PrayersNotFoundError(city_name, date)
        rows = next(iter(
            row
            for row in tree.xpath("//section[@id='content-tab1']//tbody/tr")
            if row.xpath('./td')[0].text == str(date.day)
        ))
        return PrayerMessageTextDict({
            'city_name': tree.xpath('//h1/text()')[0].split('.')[0],
            'date': date.strftime('%d.%m.%Y'),
            'fajr_prayer_time': rows[1].text,
            'sunrise_prayer_time': rows[2].text,
            'dhuhr_prayer_time': rows[3].text,
            'asr_prayer_time': rows[4].text,
            'magrib_prayer_time': rows[5].text,
            'ishaa_prayer_time': rows[6].text,
        })
