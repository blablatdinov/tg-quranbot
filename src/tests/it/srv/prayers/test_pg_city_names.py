# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
