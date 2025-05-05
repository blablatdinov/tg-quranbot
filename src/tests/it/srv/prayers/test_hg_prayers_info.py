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
from pathlib import Path

import httpx
import pytest

from srv.prayers.fk_city import FkCity
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.hg_prayers_info import HgPrayersInfo


@pytest.fixture
def hg_mock(respx_mock):
    respx_mock.get('https://halalguide.me/kazan/namaz-time/may-2025').mock(return_value=httpx.Response(
        200,
        text=Path('src/tests/fixtures/hg_response.html').read_text(encoding='utf-8'),
    ))


@pytest.fixture
async def city(city_factory, pgsql):
    city_id = uuid.uuid4()
    await city_factory(str(city_id), 'Казань')
    # TODO #1672:30min создать таблицу в БД для хранения url
    # await pgsql.execute(  # noqa: ERA001
    #     'INSERT INTO namaz_today_cities (city_id, link) VALUES (:city_id, :link)',  # noqa: ERA001
    #     {'city_id': str(city_id), 'link': 'https://namaz.today/city/kazan'},  # noqa: ERA001
    # )  # noqa: ERA001
    return FkCity(city_id, 'Казань')


# TODO #1672:30min Исправить тесты и убрать маркер skip
@pytest.mark.skip
@pytest.mark.usefixtures('hg_mock')
async def test_today(time_machine, pgsql, city):
    time_machine.move_to('2025-01-06')
    got = await HgPrayersInfo(
        city,
        FkPrayerDate(datetime.date(2025, 1, 6)),
        pgsql,
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


@pytest.mark.usefixtures('hg_mock')
@pytest.mark.skip
async def test_by_date(pgsql, time_machine, city):
    time_machine.move_to('2025-01-14')
    got = await HgPrayersInfo(
        city,
        FkPrayerDate(datetime.date(2025, 1, 20)),
        pgsql,
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
