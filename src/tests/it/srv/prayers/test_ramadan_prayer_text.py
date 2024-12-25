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

import pytz

from app_types.fk_async_str import FkAsyncStr
from app_types.fk_update import FkUpdate
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.prayers_text import PrayersText
from srv.prayers.ramadan_prayer_text import RamadanPrayerText


async def test(pgsql, prayers_factory):
    await prayers_factory('2023-12-19')
    got = await RamadanPrayerText(
        PrayersText(
            pgsql,
            FkPrayerDate(datetime.datetime(2023, 12, 19, tzinfo=pytz.timezone('Europe/Moscow'))),
            FkAsyncStr('080fd3f4-678e-4a1c-97d2-4460700fe7ac'),
            FkUpdate('{"message":{"text":"Время намаза"}}'),
        ),
        ramadan_mode=True,
    ).to_str()

    assert got == '\n'.join([
        'Время намаза для г. Kazan (19.12.2023)\n',
        'Иртәнге: 05:43 <i>- Конец сухура</i>',
        'Восход: 08:02',
        'Өйлә: 12:00',
        'Икенде: 13:21',
        'Ахшам: 15:07 <i>- Ифтар</i>',
        'Ястү: 17:04',
    ])
