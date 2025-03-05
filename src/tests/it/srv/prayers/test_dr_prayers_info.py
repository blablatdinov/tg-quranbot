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
from pathlib import Path

import httpx
import pytest

from srv.prayers.dr_prayers_info import DrPrayersInfo
from srv.prayers.fk_city import FkCity
from srv.prayers.fk_prayer_date import FkPrayerDate


@pytest.fixture
def dr_mock(respx_mock):
    respx_mock.get('https://dumrt.ru/netcat_files/391/638/Kazan.csv?t=050325').mock(return_value=httpx.Response(
        200,
        text=Path('src/tests/fixtures/dr_response.csv').read_text(encoding='utf-8'),
    ))


@pytest.mark.usefixtures('dr_mock')
async def test_today(time_machine, pgsql):
    time_machine.move_to('2025-01-06')
    got = await DrPrayersInfo(
        FkCity('', 'Казань'),
        FkPrayerDate(datetime.date(2025, 1, 6)),
        pgsql,
    ).to_dict()

    assert got == {
        'asr_prayer_time': '13:32',
        'city_name': 'Казань',
        'date': '06.01.2025',
        'dhuhr_prayer_time': '11:46',
        'fajr_prayer_time': '05:53',
        'ishaa_prayer_time': '17:17',
        'magrib_prayer_time': '15:20',
        'sunrise_prayer_time': '08:13',
    }
