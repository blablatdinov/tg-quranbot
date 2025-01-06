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

    assert got == {
        'asr_prayer_time': '14:35',
        'city_name': 'Казань',
        'date': '21.10.2023',
        'dhuhr_prayer_time': '12:00',
        'fajr_prayer_time': '04:22 <i>- Конец сухура</i>',
        'ishaa_prayer_time': '18:12',
        'magrib_prayer_time': '16:30 <i>- Ифтар</i>',
        'sunrise_prayer_time': '06:26',
    }
