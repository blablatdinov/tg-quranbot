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
import datetime

import pytest
import pytz

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from handlers.concrete_podcast_answer import ConcretePodcastAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


@pytest.fixture
async def _db_podcast_without_telegram_file_id(pgsql):
    file_id = str(uuid.uuid4())
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, NULL, 'https://link-to-file.domain', :created_at)",
        ]),
        {'file_id': file_id, 'created_at': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))},
    )
    await pgsql.execute(
        'INSERT INTO podcasts (public_id, file_id)\nVALUES (:public_id, :file_id)',
        {'public_id': str(uuid.uuid4()), 'file_id': file_id},
    )


@pytest.fixture
async def _db_podcast(pgsql, user_factory):
    file_id = str(uuid.uuid4())
    await user_factory(123)
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        {'file_id': file_id, 'created_at': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))},
    )
    await pgsql.execute(
        'INSERT INTO podcasts (public_id, file_id)\nVALUES (:public_id, :file_id)',
        {'public_id': str(uuid.uuid4()), 'file_id': file_id},
    )


@pytest.mark.usefixtures('_db_podcast')
async def test_concrete_podcast(pgsql, fake_redis):
    debug_mode = True
    got = await ConcretePodcastAnswer(
        debug_mode,
        FkAnswer(),
        fake_redis,
        pgsql,
        FkLogSink(),
    ).build(FkUpdate('{"chat":{"id":123},"message":{"text":"/podcast1"}}'))

    assert len(got) == 1
    assert got[0].url.params['text'] == 'https://link-to-file.domain'


@pytest.mark.usefixtures('_db_podcast_without_telegram_file_id')
async def test_podcast_without_tg_file_id(pgsql, fake_redis):
    debug_mode = False
    got = await ConcretePodcastAnswer(
        debug_mode,
        FkAnswer(),
        fake_redis,
        pgsql,
        FkLogSink(),
    ).build(FkUpdate('{"chat":{"id":123},"message":{"text":"/podcast1"}}'))

    assert 'audio' not in got[0].url.params
    assert got[0].url.params['text'] == 'https://link-to-file.domain'
