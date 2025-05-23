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

from srv.prayers.pg_city_names import PgCityNames


@pytest.fixture
async def _db_cities(city_factory, faker):
    await city_factory('e9fa0fff-4e6a-47c8-8654-09adf913734a', 'Казань')
    for _ in range(25):
        await city_factory(
            str(uuid.uuid4()),
            'Ка{0}'.format(faker.address()),
        )


@pytest.mark.usefixtures('_db_cities')
async def test(pgsql):
    names = await PgCityNames(pgsql, 'Каз').to_list()

    assert names == ['Казань']


@pytest.mark.usefixtures('_db_cities')
async def test_limit(pgsql):
    names = await PgCityNames(pgsql, 'ка').to_list()

    assert len(names) == 20
