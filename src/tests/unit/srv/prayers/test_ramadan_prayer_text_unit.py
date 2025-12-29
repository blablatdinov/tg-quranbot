# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from srv.prayers.fk_prayers_info import FkPrayersInfo
from srv.prayers.ramadan_prayer_info import RamadanPrayerInfo


@pytest.fixture
def prayer_time_info():
    return {
        'city_name': 'Казань',
        'date': '21.10.2023',
        'fajr_prayer_time': '04:22',
        'sunrise_prayer_time': '06:26',
        'dhuhr_prayer_time': '12:00',
        'asr_prayer_time': '14:35',
        'magrib_prayer_time': '16:30',
        'ishaa_prayer_time': '18:12',
    }


async def test_not_ramadan_mode(prayer_time_info):
    got = await RamadanPrayerInfo(
        FkPrayersInfo(prayer_time_info),
        ramadan_mode=False,
    ).to_dict()

    assert got == prayer_time_info


async def test_ramadan_mode(prayer_time_info):
    got = await RamadanPrayerInfo(
        FkPrayersInfo(prayer_time_info),
        ramadan_mode=True,
    ).to_dict()

    assert got['fajr_prayer_time'] == '04:22 <i>- Конец сухура</i>'
    assert got['magrib_prayer_time'] == '16:30 <i>- Ифтар</i>'
