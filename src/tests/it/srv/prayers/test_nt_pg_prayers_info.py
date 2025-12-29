# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
import uuid

import pytest

from exceptions.prayer_exceptions import PrayersAlreadyExistsError
from srv.prayers.fk_city import FkCity
from srv.prayers.fk_prayers_info import FkPrayersInfo
from srv.prayers.nt_pg_prayers_info import NtPgPrayersInfo


@pytest.fixture
async def _db_city(city_factory):
    await city_factory('e9fa0fff-4e6a-47c8-8654-09adf913734a', 'Казань')


@pytest.fixture
async def _user(user_factory):
    await user_factory(1, city=FkCity(uuid.UUID('e9fa0fff-4e6a-47c8-8654-09adf913734a'), 'Казань'))


@pytest.mark.usefixtures('_db_city', '_user')
async def test(pgsql):
    await NtPgPrayersInfo(
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


@pytest.mark.usefixtures('_db_city', '_user')
async def test_double(pgsql):
    nt_user_prayers_info = NtPgPrayersInfo(
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
    )
    await nt_user_prayers_info.to_dict()
    with pytest.raises(PrayersAlreadyExistsError):
        await nt_user_prayers_info.to_dict()

    assert await pgsql.fetch_val('select count(*) from prayers') == 6
