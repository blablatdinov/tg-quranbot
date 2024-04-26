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

import uuid

import pytest

from exceptions.internal_exceptions import UserNotFoundError
from srv.prayers.city import FkCity
from srv.prayers.update_user_city import PgUpdatedUserCity


@pytest.fixture()
async def _city(pgsql):
    await pgsql.execute("INSERT INTO cities (city_id, name) VALUES ('080fd3f4-678e-4a1c-97d2-4460700fe7ac', 'Kazan')")
    await pgsql.execute('INSERT INTO users (chat_id) VALUES (849357)')


@pytest.mark.usefixtures('_city')
async def test(pgsql):
    await PgUpdatedUserCity(
        FkCity(uuid.UUID('080fd3f4-678e-4a1c-97d2-4460700fe7ac'), 'Kazan'),
        849357,
        pgsql,
    ).update()

    assert await pgsql.fetch_val(
        'SELECT city_id FROM users WHERE chat_id = 849357',
    ) == '080fd3f4-678e-4a1c-97d2-4460700fe7ac'


@pytest.mark.usefixtures('_city')
async def test_user_not_found(pgsql):
    with pytest.raises(UserNotFoundError):
        await PgUpdatedUserCity(
            FkCity(uuid.UUID('080fd3f4-678e-4a1c-97d2-4460700fe7ac'), 'Kazan'),
            84935,
            pgsql,
        ).update()
