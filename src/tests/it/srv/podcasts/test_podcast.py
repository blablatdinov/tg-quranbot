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
import json
import uuid
from operator import truediv

import pytest
from furl import furl

from app_types.intable import ThroughAsyncIntable
from app_types.update import FkUpdate
from exceptions.base_exception import InternalBotError
from handlers.podcast_answer import PodcastAnswer
from integrations.tg.tg_answers import FkAnswer
from srv.podcasts.podcast import PgPodcast


@pytest.fixture()
async def _db_podcast(pgsql):
    file_id = str(uuid.uuid4())
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        {'file_id': file_id, 'created_at': datetime.datetime.now()},
    )
    await pgsql.execute(
        'INSERT INTO podcasts (public_id, file_id)\nVALUES (:public_id, :file_id)',
        {'public_id': str(uuid.uuid4()), 'file_id': file_id},
    )


@pytest.mark.parametrize(('debug_mode', 'expected'), [
    (
        False,
        (
            truediv(furl('https://some.domain'), 'sendAudio')
            .add({
                'chat_id': '123',
                'audio': 'aoiejf298jr9p23u8qr3',
                'reply_markup': json.dumps({
                    'inline_keyboard': [[
                        {'text': '👍 0', 'callback_data': 'like(1)'},
                        {'text': '👎 0', 'callback_data': 'dislike(1)'},
                    ]],
                }),
            })
        ),
    ),
    (
        True,
        (
            truediv(furl('https://some.domain'), 'sendMessage')
            .add({
                'chat_id': '123',
                'text': 'https://link-to-file.domain',
                'reply_markup': json.dumps({
                    'inline_keyboard': [[
                        {'text': '👍 0', 'callback_data': 'like(1)'},
                        {'text': '👎 0', 'callback_data': 'dislike(1)'},
                    ]],
                }),
            })
        ),
    ),
])
@pytest.mark.usefixtures('_db_podcast')
async def test(pgsql, rds, debug_mode, expected, unquote):
    got = await PodcastAnswer.random_podcast_ctor(
        debug_mode,
        FkAnswer(),
        rds,
        pgsql,
    ).build(FkUpdate('{"chat":{"id":123}}'))

    assert len(got) == 2
    assert got[0].url.params['text'] == '/podcast1'
    assert unquote(got[1].url) == unquote(expected)


async def test_podcast_not_found(pgsql):
    with pytest.raises(InternalBotError):
        await PgPodcast(ThroughAsyncIntable(1), pgsql).tg_file_id()
    with pytest.raises(InternalBotError):
        await PgPodcast(ThroughAsyncIntable(1), pgsql).file_link()
