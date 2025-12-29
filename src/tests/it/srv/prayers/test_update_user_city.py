# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from exceptions.internal_exceptions import UserNotFoundError
from srv.prayers.pg_updated_user_city import PgUpdatedUserCity


@pytest.fixture
async def city(city_factory):
    return await city_factory('080fd3f4-678e-4a1c-97d2-4460700fe7ac', 'Kazan')


@pytest.fixture
async def _user(user_factory):
    await user_factory(849357)


@pytest.mark.usefixtures('_user')
async def test(pgsql, city):
    await PgUpdatedUserCity(city, 849357, pgsql).update()

    assert await pgsql.fetch_val(
        'SELECT city_id FROM users WHERE chat_id = 849357',
    ) == await city.city_id()


@pytest.mark.usefixtures('_user')
async def test_user_not_found(pgsql, city):
    with pytest.raises(UserNotFoundError):
        await PgUpdatedUserCity(city, 84935, pgsql).update()
