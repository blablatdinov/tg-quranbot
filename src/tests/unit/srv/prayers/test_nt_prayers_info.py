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

from exceptions.prayer_exceptions import PrayersNotFoundError
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.nt_prayers_info import NtPrayersInfo


@pytest.fixture
def nt_mock(respx_mock):
    respx_mock.get('https://namaz.today/city/kazan').mock(return_value=httpx.Response(
        200,
        text=Path('src/tests/fixtures/nt_response.html').read_text(encoding='utf-8'),
    ))


@pytest.mark.usefixtures('nt_mock')
async def test_today(time_machine):
    time_machine.move_to('2025-01-06')
    got = await NtPrayersInfo(
        'kazan',
        FkPrayerDate(datetime.date(2025, 1, 6)),
    ).to_dict()

    assert got == {
        'asr_prayer_time': '13:39',
        'city_name': 'Казань',
        'date': '06.01.2025',
        'dhuhr_prayer_time': '11:50',
        'fajr_prayer_time': '05:53',
        'ishaa_prayer_time': '17:25',
        'magrib_prayer_time': '15:28',
        'sunrise_prayer_time': '08:11',
    }


@pytest.mark.usefixtures('nt_mock')
async def test_by_date():
    got = await NtPrayersInfo(
        'kazan',
        FkPrayerDate(datetime.date(2025, 1, 20)),
    ).to_dict()

    assert got == {
        'asr_prayer_time': '14:02',
        'city_name': 'Казань',
        'date': '20.01.2025',
        'dhuhr_prayer_time': '11:56',
        'fajr_prayer_time': '05:44',
        'ishaa_prayer_time': '17:44',
        'magrib_prayer_time': '15:53',
        'sunrise_prayer_time': '07:57',
    }


# TODO #1450:30min Пока возможно получать время намаза только в рамках текущего месяца.
#  В таблице на странице https://namaz.today/city/kazan приведены данные только на текущий месяц
#  Оставил коммент с вопросом, пока ждем решения
@pytest.mark.usefixtures('nt_mock')
async def test_unavailable_date():
    with pytest.raises(PrayersNotFoundError):
        await NtPrayersInfo(
            'kazan',
            FkPrayerDate(datetime.date(2025, 2, 20)),
        ).to_dict()
