# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

from srv.ayats.favorites.user_favorite_ayats import UserFavoriteAyats


@pytest.fixture
async def _favorite_ayats(db_ayat, pgsql, user_factory):
    await user_factory(49573)
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO favorite_ayats (user_id, ayat_id) VALUES',
            '(49573, :ayat_id)',
        ]),
        {'ayat_id': await db_ayat.identifier().ayat_id()},
    )


@pytest.mark.usefixtures('_favorite_ayats')
async def test_user_favorite_ayats(pgsql):
    got = await UserFavoriteAyats(pgsql, 49573).to_list()

    assert [await ayat.identifier().ayat_id() for ayat in got] == [1]
