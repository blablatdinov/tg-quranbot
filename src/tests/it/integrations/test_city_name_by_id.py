# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_async_str import FkAsyncStr
from exceptions.content_exceptions import CityNotSupportedError
from integrations.city_name_by_id import CityNameById


@pytest.fixture
async def _db_city(pgsql):
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO cities (city_id, name)',
            'VALUES',
            "('7ceb19b6-93ff-4819-bed7-86f14077af9a', 'Kazan')",
        ]),
    )


@pytest.mark.usefixtures('_db_city')
async def test(pgsql):
    got = await CityNameById(
        pgsql,
        FkAsyncStr('7ceb19b6-93ff-4819-bed7-86f14077af9a'),
    ).to_str()

    assert got == 'Kazan'


@pytest.mark.usefixtures('_db_city')
async def test_not_found(pgsql):
    with pytest.raises(CityNotSupportedError):
        await CityNameById(
            pgsql,
            FkAsyncStr(''),
        ).to_str()
