# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from srv.podcasts.podcast_id import PodcastId


@pytest.fixture
async def _db_podcast(pgsql, user_factory):
    await user_factory(7485394)
    await pgsql.execute('\n'.join([
        'INSERT INTO files (file_id, created_at)',
        "VALUES ('818dfe43-3a21-49d7-ada4-826443d20991', '2024-10-29')",
    ]))
    await pgsql.execute('\n'.join([
        'INSERT INTO podcasts (podcast_id, file_id)',
        "VALUES (759, '818dfe43-3a21-49d7-ada4-826443d20991')",
    ]))


@pytest.mark.usefixtures('_db_podcast')
async def test(pgsql):
    podcast_id = PodcastId(pgsql, 7485394)

    assert await podcast_id.to_int() == 759
