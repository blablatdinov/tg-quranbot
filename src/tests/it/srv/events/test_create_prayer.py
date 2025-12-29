# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
