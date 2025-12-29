# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
