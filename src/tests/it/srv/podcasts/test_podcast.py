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

# flake8: noqa: WPS202
import datetime
import uuid
from operator import truediv

import pytest
import pytz
import ujson
from furl import furl

from app_types.fk_async_int import FkAsyncInt
from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from exceptions.base_exception import InternalBotError
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.podcasts.pg_podcast import PgPodcast
from srv.podcasts.random_podcast_answer import RandomPodcastAnswer


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


@pytest.fixture
async def _podcast_reactions(pgsql, user_factory):
    file_ids = [str(uuid.uuid4()) for _ in range(3)]
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        [
            {'file_id': file_id, 'created_at': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))}
            for file_id in file_ids
        ],
    )
    await pgsql.execute_many(
        'INSERT INTO podcasts (file_id) VALUES (:file_id)',
        [{'file_id': file_id} for file_id in file_ids],
    )
    await user_factory(937584)
    await user_factory(87945)
    await pgsql.execute_many(
        'INSERT INTO podcast_reactions (podcast_id, reaction, user_id) VALUES (:podcast_id, :reaction, :user_id)',
        [
            {'podcast_id': 1, 'reaction': 'showed', 'user_id': 937584},
            {'podcast_id': 2, 'reaction': 'like', 'user_id': 937584},
            {'podcast_id': 1, 'reaction': 'showed', 'user_id': 87945},
            {'podcast_id': 2, 'reaction': 'dislike', 'user_id': 87945},
            {'podcast_id': 3, 'reaction': 'like', 'user_id': 87945},
        ],
    )


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


@pytest.mark.parametrize(('debug_mode', 'expected'), [
    (
        False,
        (
            truediv(furl('https://some.domain'), 'sendAudio')
            .add({
                'chat_id': '123',
                'audio': 'aoiejf298jr9p23u8qr3',
                'reply_markup': ujson.dumps({
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
                'reply_markup': ujson.dumps({
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
async def test_random_podcast(pgsql, fake_redis, debug_mode, expected, unquote):
    got = await RandomPodcastAnswer(
        debug_mode,
        FkAnswer(),
        fake_redis,
        pgsql,
        FkLogSink(),
    ).build(FkUpdate('{"chat":{"id":123}}'))

    assert len(got) == 2
    assert got[0].url.params['text'] == '/podcast1'
    assert unquote(got[1].url) == unquote(expected)


async def test_podcast_not_found(pgsql):
    with pytest.raises(InternalBotError):
        await PgPodcast(FkAsyncInt(1), pgsql).tg_file_id()
    with pytest.raises(InternalBotError):
        await PgPodcast(FkAsyncInt(1), pgsql).file_link()


@pytest.mark.usefixtures('_podcast_reactions')
async def test_ignore_showed_podcasts(fake_redis, pgsql, unquote):
    debug_mode = False
    got = await RandomPodcastAnswer(
        debug_mode,
        FkAnswer(),
        fake_redis,
        pgsql,
        FkLogSink(),
    ).build(FkUpdate('{"chat":{"id":937584}}'))

    assert unquote(
        got[0].url.query.decode('utf-8'),
    )[20:] == '/podcast3'


@pytest.mark.usefixtures('_podcast_reactions')
async def test_all_podcasts_showed(fake_redis, pgsql, unquote):
    debug_mode = False
    random_podcast_answer = RandomPodcastAnswer(
        debug_mode,
        FkAnswer(),
        fake_redis,
        pgsql,
        FkLogSink(),
    )
    answer1 = await random_podcast_answer.build(FkUpdate('{"chat":{"id":87945}}'))

    assert '/podcast' in unquote(answer1[0].url.query.decode('utf-8'))
