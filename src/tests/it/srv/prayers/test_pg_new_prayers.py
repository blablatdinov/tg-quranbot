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

import uuid

import pytest

from srv.prayers.pg_new_prayers import PgNewPrayers


@pytest.fixture
async def city(city_factory):
    await city_factory(str(uuid.uuid4()), 'Казань')


# TODO #1428:30min решить проблему с созданием намазов и снять маркер skip
# TODO #1428:30min написать assert
@pytest.mark.skip
async def test(pgsql, city):
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
