# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_async_str import FkAsyncStr
from integrations.tg.fk_coordinates import FkCoordinates
from srv.prayers.pg_city import PgCity


@pytest.fixture
async def _db_city(city_factory):
    await city_factory('e9fa0fff-4e6a-47c8-8654-09adf913734a', 'Казань')


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
