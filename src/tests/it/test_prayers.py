"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import datetime
import uuid

import httpx
import pytest

from app_types.update import FkUpdate
from handlers.podcast_answer import PodcastAnswer
from integrations.tg.tg_answers import FkAnswer
from repository.podcast import RandomPodcast


@pytest.fixture()
async def db_podcast(pgsql):
    file_id = str(uuid.uuid4())
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        {'file_id': file_id, 'created_at': datetime.datetime.now()},
    )
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO podcasts (podcast_id, file_id)',
            'VALUES (:podcast_id, :file_id)',
        ]),
        {'podcast_id': str(uuid.uuid4()), 'file_id': file_id},
    )


@pytest.mark.parametrize('debug_mode,expected', [
    (False, httpx.URL('https://some.domain/sendAudio?chat_id=123&audio=aoiejf298jr9p23u8qr3')),
    (True, httpx.URL('https://some.domain/sendMessage?chat_id=123&text=https%3A%2F%2Flink-to-file.domain')),
])
async def test(db_podcast, pgsql, rds, debug_mode, expected):
    got = await PodcastAnswer(
        debug_mode,
        FkAnswer(),
        RandomPodcast(pgsql),
        rds,
    ).build(FkUpdate('{"chat":{"id":123}}'))

    assert got[0].url == expected
