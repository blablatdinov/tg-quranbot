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

from srv.prayers.fk_city import FkCity
from srv.prayers.nt_prayers_url import NtPrayersUrl


@pytest.fixture
async def city(city_factory, pgsql):
    city_id = uuid.uuid4()
    await city_factory(str(city_id), 'Иннополис')
    await pgsql.execute(
        'INSERT INTO namaz_today_cities (city_id, link) VALUES (:city_id, :link)',
        {'city_id': str(city_id), 'link': 'https://namaz.today/city/innopolis'},
    )
    return FkCity(city_id, 'Иннополис')


async def test(pgsql, city):
    got = await NtPrayersUrl(
        city,
        pgsql,
    ).to_str()

    assert got == 'https://namaz.today/city/innopolis'
