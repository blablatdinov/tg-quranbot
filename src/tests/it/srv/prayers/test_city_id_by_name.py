# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_async_str import FkAsyncStr
from exceptions.content_exceptions import CityNotSupportedError
from srv.prayers.city_id_by_name import CityIdByName


@pytest.fixture
async def _db_city(city_factory):
    await city_factory('e9fa0fff-4e6a-47c8-8654-09adf913734a', 'Казань')


@pytest.mark.usefixtures('_db_city')
async def test_city_id_by_name(pgsql):
    got = await CityIdByName(FkAsyncStr('Казань'), pgsql).to_str()

    assert got == 'e9fa0fff-4e6a-47c8-8654-09adf913734a'


@pytest.mark.usefixtures('_db_city')
async def test_city_id_by_name_not_found(pgsql):
    with pytest.raises(CityNotSupportedError):
        await CityIdByName(FkAsyncStr('Nab'), pgsql).to_str()
