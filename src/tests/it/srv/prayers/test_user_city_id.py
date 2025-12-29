# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from srv.prayers.user_city_id import UserCityId


@pytest.fixture
async def _db_city(city_factory, user_factory):
    city = await city_factory('e9fa0fff-4e6a-47c8-8654-09adf913734a', 'Казань')
    await user_factory(89348, city=city)


@pytest.mark.usefixtures('_db_city')
async def test(pgsql):
    got = await UserCityId(pgsql, 89348).to_str()

    assert got == 'e9fa0fff-4e6a-47c8-8654-09adf913734a'
