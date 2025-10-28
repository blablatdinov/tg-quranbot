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
import uuid

import pytest

from srv.prayers.pg_new_prayers import PgNewPrayers


@pytest.fixture
async def city(city_factory):
    return await city_factory(str(uuid.uuid4()), 'Казань')


async def test(pgsql, city):
    city_id = await city.city_id()
    await PgNewPrayers(
        {
            'asr_prayer_time': '13:39',
            'city_name': 'Казань',
            'date': '06.01.2025',
            'dhuhr_prayer_time': '11:50',
            'fajr_prayer_time': '05:53',
            'ishaa_prayer_time': '17:25',
            'magrib_prayer_time': '15:28',
            'sunrise_prayer_time': '08:11',
        },
        pgsql,
    ).create()

    # TODO #1525:30min проверить правильно ли сохраняется время в БД
    assert [
        dict(row)
        for row in await pgsql.fetch_all(
            'SELECT city_id, day, name, time FROM prayers',
        )
    ] == [
        {
            'city_id': city_id,
            'day': datetime.date(2025, 1, 6),
            'name': 'fajr',
            'time': datetime.time(5, 53),
        },
        {
            'city_id': city_id,
            'day': datetime.date(2025, 1, 6),
            'name': 'sunrise',
            'time': datetime.time(8, 11),
        },
        {
            'city_id': city_id,
            'day': datetime.date(2025, 1, 6),
            'name': 'dhuhr',
            'time': datetime.time(11, 50),
        },
        {
            'city_id': city_id,
            'day': datetime.date(2025, 1, 6),
            'name': 'asr',
            'time': datetime.time(13, 39),
        },
        {
            'city_id': city_id,
            'day': datetime.date(2025, 1, 6),
            'name': 'maghrib',
            'time': datetime.time(15, 28),
        },
        {
            'city_id': city_id,
            'day': datetime.date(2025, 1, 6),
            'name': "isha'a",
            'time': datetime.time(17, 25),
        },
    ]
