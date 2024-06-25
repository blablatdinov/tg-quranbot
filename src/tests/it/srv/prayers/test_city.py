# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

from app_types.FkAsyncStr import FkAsyncStr
from exceptions.content_exceptions import CityNotSupportedError
from integrations.tg.FkCoordinates import FkCoordinates
from srv.prayers.city_id_by_name import CityIdByName
from srv.prayers.pg_city import PgCity


@pytest.fixture()
async def _db_city(pgsql):
    await pgsql.execute("INSERT INTO cities (city_id, name) VALUES (:city_id, 'Казань')", {
        'city_id': 'e9fa0fff-4e6a-47c8-8654-09adf913734a',
    })


@pytest.mark.usefixtures('_db_city')
async def test_city_id_by_name(pgsql):
    got = await CityIdByName(FkAsyncStr('Казань'), pgsql).to_str()

    assert got == 'e9fa0fff-4e6a-47c8-8654-09adf913734a'


@pytest.mark.usefixtures('_db_city')
async def test_city_id_by_name_not_found(pgsql):
    with pytest.raises(CityNotSupportedError):
        await CityIdByName(FkAsyncStr('Nab'), pgsql).to_str()


@pytest.mark.usefixtures('_db_city')
async def test_pg_city(pgsql):
    city = PgCity(FkAsyncStr('e9fa0fff-4e6a-47c8-8654-09adf913734a'), pgsql)

    assert str(await city.city_id()) == 'e9fa0fff-4e6a-47c8-8654-09adf913734a'
    assert await city.name() == 'Казань'


@pytest.mark.usefixtures('_db_city', '_mock_nominatim')
async def test_ctors(pgsql):
    city_by_name = PgCity.name_ctor('Казань', pgsql)
    city_by_location = PgCity.location_ctor(FkCoordinates(55.7887, 49.1221), pgsql)

    assert str(await city_by_name.city_id()) == str(await city_by_location.city_id())
