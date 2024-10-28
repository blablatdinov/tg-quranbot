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

from integrations.city_name_by_id import CityNameById
from app_types.fk_async_str import FkAsyncStr
from exceptions.content_exceptions import CityNotSupportedError


@pytest.fixture
async def _db_city(pgsql):
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO cities (city_id, name)',
            'VALUES',
            "('7ceb19b6-93ff-4819-bed7-86f14077af9a', 'Erak')",
        ])
    )


@pytest.mark.usefixtures('_db_city')
async def test(pgsql):
    got = await CityNameById(
        pgsql,
        FkAsyncStr('7ceb19b6-93ff-4819-bed7-86f14077af9a'),
    ).to_str()

    assert got == 'Erak'


@pytest.mark.usefixtures('_db_city')
async def test_not_found(pgsql):
    with pytest.raises(CityNotSupportedError):
        await CityNameById(
            pgsql,
            FkAsyncStr(''),
        ).to_str()
