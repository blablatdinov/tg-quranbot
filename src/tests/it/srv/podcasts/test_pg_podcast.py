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

from srv.podcasts.pg_podcast import PgPodcast
from app_types.fk_async_int import FkAsyncInt


@pytest.fixture
async def _db_podcast(pgsql):
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
    podcast = PgPodcast(FkAsyncInt(759), pgsql)

    assert await podcast.podcast_id() == 759