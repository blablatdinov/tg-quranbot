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

import datetime
import uuid

import pytest
import pytz
import ujson

from app_types.fk_log_sink import FkLogSink
from app_types.update import FkUpdate
from handlers.podcast_reaction_change_answer import PodcastReactionChangeAnswer
from integrations.tg.tg_answers import FkAnswer


@pytest.fixture()
async def _once_podcast(pgsql):
    file_id = str(uuid.uuid4())
    await pgsql.execute('INSERT INTO users (chat_id) VALUES (905)')
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        {'file_id': file_id, 'created_at': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))},
    )
    await pgsql.execute(
        'INSERT INTO podcasts (podcast_id, public_id, file_id) VALUES (:podcast_id, :public_id, :file_id)',
        {'podcast_id': 5, 'public_id': str(uuid.uuid4()), 'file_id': file_id},
    )


@pytest.fixture()
async def _podcasts(pgsql):
    file_ids = [uuid.uuid4() for _ in range(3)]
    await pgsql.execute_many('INSERT INTO files (file_id, created_at) VALUES (:file_id, :created_at)', [
        {
            'file_id': str(file_id),
            'created_at': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')),
        }
        for file_id in file_ids
    ])
    await pgsql.execute_many('INSERT INTO podcasts (podcast_id, file_id) VALUES (:podcast_id, :file_id)', [
        {
            'podcast_id': podcast_id,
            'file_id': str(file_id),
        } for podcast_id, file_id in enumerate(file_ids, start=1)
    ])
    await pgsql.execute('INSERT INTO users (chat_id) VALUES (1)')


@pytest.fixture()
async def _existed_reaction(pgsql, _podcasts):
    query = '\n'.join([
        'INSERT INTO podcast_reactions (user_id, podcast_id, reaction)',
        "VALUES (1, 1, 'like')",
    ])
    await pgsql.execute(query)
    query = '\n'.join([
        'INSERT INTO podcast_reactions (user_id, podcast_id, reaction)',
        "VALUES (1, 2, 'dislike')",
    ])
    await pgsql.execute(query)


@pytest.mark.usefixtures('_once_podcast')
async def test_without_message_text(pgsql, fake_redis):
    """Случай без текста в update.

    Почему-то телеграм не присылает текст сообщения спустя время
    """
    debug = False
    got = await PodcastReactionChangeAnswer(debug, FkAnswer(), fake_redis, pgsql, FkLogSink()).build(
        FkUpdate(ujson.dumps({
            'callback_query': {
                'from': {'id': 905},
                'message': {
                    'message_id': 496344,
                    'chat': {'id': 905},
                    'date': 0,
                },
                'chat_instance': '-8563585384798880073',
                'data': 'mark_readed(5)',
            },
        })),
    )

    assert got[0].url.path == '/sendMessage'
    assert got[0].url.params['text'] == '/podcast5'
    assert got[1].url.params['reply_markup'] == ujson.dumps({
        'inline_keyboard': [[
            {'text': '👍 1', 'callback_data': 'like(5)'}, {'text': '👎 0', 'callback_data': 'dislike(5)'},
        ]],
    })


@pytest.mark.usefixtures('_once_podcast')
async def test_without_message_with_audio(pgsql, fake_redis):
    debug = False
    got = await PodcastReactionChangeAnswer(debug, FkAnswer(), fake_redis, pgsql, FkLogSink()).build(
        FkUpdate(ujson.dumps({
            'callback_query': {
                'from': {'id': 905},
                'message': {
                    'message_id': 743895,
                    'audio': {},
                    'chat': {'id': 905},
                    'date': 0,
                },
                'chat_instance': '-8563585384798880073',
                'data': 'mark_readed(5)',
            },
        })),
    )

    assert got[0].url.path == '/editMessageReplyMarkup'
    assert got[0].url.params['reply_markup'] == ujson.dumps({
        'inline_keyboard': [[
            {'text': '👍 1', 'callback_data': 'like(5)'}, {'text': '👎 0', 'callback_data': 'dislike(5)'},
        ]],
    })


@pytest.mark.usefixtures('_existed_reaction')
@pytest.mark.parametrize(('podcast_id', 'reaction', 'button1', 'button2'), [
    (1, 'like', '👍 0', '👎 0'),
    (1, 'dislike', '👍 0', '👎 1'),
    (2, 'like', '👍 1', '👎 0'),
    (2, 'dislike', '👍 0', '👎 0'),
    (3, 'like', '👍 1', '👎 0'),
    (3, 'dislike', '👍 0', '👎 1'),
])
async def test(pgsql, fake_redis, reaction, podcast_id, button1, button2):
    debug = True
    got = await PodcastReactionChangeAnswer(
        debug, FkAnswer(), fake_redis, pgsql, FkLogSink(),
    ).build(FkUpdate(
        ujson.dumps({
            'chat': {'id': 1},
            'callback_query': {'data': '{0}({1})'.format(reaction, podcast_id)},
            'message': {'message_id': 1, 'text': '/podcast{0}'.format(podcast_id)},
        }),
    ))

    assert len(got) == 1
    assert ujson.loads(got[0].url.params['reply_markup']) == {
        'inline_keyboard': [[
            {'callback_data': 'like({0})'.format(podcast_id), 'text': button1},
            {'callback_data': 'dislike({0})'.format(podcast_id), 'text': button2},
        ]],
    }
