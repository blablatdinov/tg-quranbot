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
from eljson.json_doc import JsonDoc

from srv.events.prayer_created_event import PrayerCreatedEvent


@pytest.fixture
async def _city(city_factory):
    await city_factory('6a4e14a7-b05d-4769-b801-e0c0dbf3c923', 'Name')


@pytest.mark.usefixtures('_city')
async def test(pgsql):
    await PrayerCreatedEvent(pgsql).process(JsonDoc({
        'data': {
            'name': 'fajr',
            'time': '5:36',
            'city_id': '6a4e14a7-b05d-4769-b801-e0c0dbf3c923',
            'day': '2023-01-02',
        },
    }))

    row = await pgsql.fetch_one('SELECT name, time, city_id, day FROM prayers')
    assert {
        key: row[key]
        for key in ('name', 'time', 'city_id', 'day')
    } == {
        'name': 'fajr',
        'time': datetime.time(5, 36),
        'city_id': '6a4e14a7-b05d-4769-b801-e0c0dbf3c923',
        'day': datetime.date(2023, 1, 2),
    }
