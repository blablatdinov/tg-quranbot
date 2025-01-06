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
from lxml import etree

from app_types.async_supports_str import AsyncSupportsStr
from app_types.fk_update import FkUpdate
from exceptions.prayer_exceptions import PrayersNotFoundError
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
class NtPrayersText(AsyncSupportsStr):
    """Текст сообщения с намазами с сайта https://namaz.today ."""

    _city_name: str
    _date: PrayerDate

    # TODO #1450:30min Исправить сложность функции (WPS210) и удалить noqa комментарий
    #  Возможно поможет решение #1438
    @override
    async def to_str(self) -> str:  # noqa: WPS210
        """Строковое представление.

        :return: str
        :raises PrayersNotFoundError: намазы не найдены
        """
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get('https://namaz.today/city/{0}'.format(self._city_name))
            response.raise_for_status()
        tree = etree.fromstring(response.text, etree.HTMLParser())  # noqa: S320. Trust https://namaz.today
        table_rows = tree.xpath("//section[@id='content-tab1']//tbody/tr")
        date = await self._date.parse(FkUpdate.empty_ctor())
        if date.month != datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).month:
            raise PrayersNotFoundError(self._city_name, date)
        for row in table_rows:
            if row.xpath('./td')[0].text == str(date.day):
                rows = row.xpath('./td')
                break
        template = '\n'.join([
            'Время намаза для г. {city_name} ({date})\n',
            'Иртәнге: {fajr_prayer_time}',
            'Восход: {sunrise_prayer_time}',
            'Өйлә: {dhuhr_prayer_time}',
            'Икенде: {asr_prayer_time}',
            'Ахшам: {magrib_prayer_time}',
            'Ястү: {ishaa_prayer_time}',
        ])
        # TODO #1428:30min Написать декоратор, который будет создавать запись prayer_at_user
        # TODO #1428:30min Определить как получать время намаза по дате
        return template.format(
            # TODO #1435:30min заменить self._city_name
            #  в аттрибуте лежит slug для города, а не название, которое
            #  должен видеть пользователь
            city_name=self._city_name,
            date=date.strftime('%d.%m.%Y'),
            fajr_prayer_time=rows[1].text,
            sunrise_prayer_time=rows[2].text,
            dhuhr_prayer_time=rows[3].text,
            asr_prayer_time=rows[4].text,
            magrib_prayer_time=rows[5].text,
            ishaa_prayer_time=rows[6].text,
        )
