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

import pytest

from srv.prayers.fk_prayers_info import FkPrayersInfo
from srv.prayers.nt_user_prayers_info import NtUserPrayersInfo
from srv.prayers.fk_city import FkCity
from integrations.tg.fk_chat_id import FkChatId


@pytest.fixture
async def _db_city(city_factory):
    await city_factory('e9fa0fff-4e6a-47c8-8654-09adf913734a', 'Казань')


@pytest.fixture
async def _user(user_factory):
    await user_factory(1, city=FkCity('e9fa0fff-4e6a-47c8-8654-09adf913734a', 'Казань'))


@pytest.mark.usefixtures('_db_city', '_user')
async def test(pgsql):
    await NtUserPrayersInfo(
        FkPrayersInfo({
            'city_name': 'Казань',
            'date': '21.10.2023',
            'fajr_prayer_time': '04:22',
            'sunrise_prayer_time': '06:26',
            'dhuhr_prayer_time': '12:00',
            'asr_prayer_time': '14:35',
            'magrib_prayer_time': '16:30',
            'ishaa_prayer_time': '18:12',
        }),
        pgsql,
        FkChatId(1),
    ).to_dict()

    assert [dict(row) for row in await pgsql.fetch_all('select city_id, day, name, time from prayers')] == [
        {
            'city_id': 'e9fa0fff-4e6a-47c8-8654-09adf913734a',
            'day': datetime.date(2023, 10, 21),
            'name': 'fajr',
            'time': datetime.time(4, 22),
        },
        {
            'city_id': 'e9fa0fff-4e6a-47c8-8654-09adf913734a',
            'day': datetime.date(2023, 10, 21),
            'name': 'sunrise',
            'time': datetime.time(6, 26),
        },
        {
            'city_id': 'e9fa0fff-4e6a-47c8-8654-09adf913734a',
            'day': datetime.date(2023, 10, 21),
            'name': 'dhuhr',
            'time': datetime.time(12, 0),
        },
        {
            'city_id': 'e9fa0fff-4e6a-47c8-8654-09adf913734a',
            'day': datetime.date(2023, 10, 21),
            'name': 'asr',
            'time': datetime.time(14, 35),
        },
        {
            'city_id': 'e9fa0fff-4e6a-47c8-8654-09adf913734a',
            'day': datetime.date(2023, 10, 21),
            'name': 'maghrib',
            'time': datetime.time(16, 30),
        },
        {
            'city_id': 'e9fa0fff-4e6a-47c8-8654-09adf913734a',
            'day': datetime.date(2023, 10, 21),
            'name': "isha'a",
            'time': datetime.time(18, 12),
        },
    ]
    assert [
        dict(row)
        for row in await pgsql.fetch_all('select user_id, is_read from prayers_at_user')
    ] == [
        {
            'is_read': False,
            'user_id': 1,
        }
        for _ in range(5)
    ]
