# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime

import pytz

from app_types.fk_async_str import FkAsyncStr
from app_types.fk_update import FkUpdate
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.pg_prayers_info import PgPrayersInfo
from srv.prayers.ramadan_prayer_info import RamadanPrayerInfo


async def test(pgsql, prayers_factory):
    await prayers_factory('2023-12-19')
    got = await RamadanPrayerInfo(
        PgPrayersInfo(
            pgsql,
            FkPrayerDate(datetime.datetime(2023, 12, 19, tzinfo=pytz.timezone('Europe/Moscow'))),
            FkAsyncStr('080fd3f4-678e-4a1c-97d2-4460700fe7ac'),
            FkUpdate('{"message":{"text":"Время намаза"}}'),
        ),
        ramadan_mode=True,
    ).to_dict()

    assert got == {
        'asr_prayer_time': '13:21',
        'city_name': 'Kazan',
        'date': '19.12.2023',
        'dhuhr_prayer_time': '12:00',
        'fajr_prayer_time': '05:43 <i>- Конец сухура</i>',
        'ishaa_prayer_time': '17:04',
        'magrib_prayer_time': '15:07 <i>- Ифтар</i>',
        'sunrise_prayer_time': '08:02',
    }
