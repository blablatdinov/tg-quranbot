# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
