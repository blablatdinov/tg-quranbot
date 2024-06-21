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

import datetime
import uuid

import pytest

from srv.prayers.city import FkCity
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser
from srv.prayers.update_user_city import PgUpdatedUserCity
from srv.users.pg_user import PgUser


@pytest.fixture()
async def cities(pgsql):
    await pgsql.execute_many(
        'INSERT INTO cities (city_id, name) VALUES (:city_id, :name)',
        [
            {'city_id': city_id, 'name': city_name}
            for city_id, city_name in (
                ('e22d9142-a39b-4e99-92f7-2082766f0987', 'Kazan'),
                ('4bd2af2a-aec9-4660-b710-405940f6e578', 'NabChelny'),
            )
        ],
    )
    return (
        FkCity(
            uuid.UUID('e22d9142-a39b-4e99-92f7-2082766f0987'),
            'Kazan',
        ),
        FkCity(
            uuid.UUID('4bd2af2a-aec9-4660-b710-405940f6e578'),
            'NabChelny',
        ),
    )


@pytest.fixture()
async def user(pgsql, cities):
    await pgsql.execute(
        'INSERT INTO users (chat_id, is_active, day, city_id) VALUES (:chat_id, :is_active, :day, :city_id)',
        {'chat_id': 849375, 'is_active': True, 'day': 2, 'city_id': await cities[0].city_id()},
    )
    return PgUser.int_ctor(849375, pgsql)


@pytest.mark.usefixtures('_prayers')
@pytest.mark.skip()
async def test(pgsql, user, cities):
    await PgNewPrayersAtUser(
        await user.chat_id(),
        pgsql,
    ).create(datetime.date(2024, 6, 5))
    await PgUpdatedUserCity(
        cities[1],
        await user.chat_id(),
        pgsql,
    ).update()
    await PgNewPrayersAtUser(
        await user.chat_id(),
        pgsql,
    ).create(datetime.date(2024, 6, 5))

    assert await pgsql.fetch_val('SELECT COUNT(*) FROM prayers_at_user') == 5
