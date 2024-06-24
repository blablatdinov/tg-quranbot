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
import ujson
from furl import furl

from app_types.logger import FkLogSink
from app_types.update import FkUpdate
from handlers.full_start_answer import FullStartAnswer
from integrations.tg.tg_answers import FkAnswer
from srv.events.sink import FkSink


@pytest.fixture()
async def _existed_user(pgsql):
    await pgsql.execute(
        'INSERT INTO users (chat_id, day, legacy_id) VALUES (321, 2, 1)',
    )


@pytest.fixture()
async def _admin_message(pgsql):
    await pgsql.execute(
        "INSERT INTO admin_messages (key, text) VALUES ('start', 'start admin message')",
    )


@pytest.mark.usefixtures('db_ayat', '_admin_message')
async def test(pgsql, fake_redis, unquote, settings_ctor):
    got = await FullStartAnswer(
        pgsql, FkAnswer(), FkSink(), fake_redis, settings_ctor(), FkLogSink(),
    ).build(FkUpdate('{"message":{"text":"/start"},"chat":{"id":321},"date":0}'))

    assert len(got) == 3
    assert unquote(got[0].url) == unquote(
        furl('https://some.domain/sendMessage')
        .add({
            'parse_mode': 'html',
            'text': 'start admin message',
            'chat_id': 321,
            'reply_markup': ujson.dumps({
                'keyboard': [
                    ['🎧 Подкасты'],
                    ['🕋 Время намаза', '🏘️ Поменять город'],
                    ['🌟 Избранное', '🔍 Найти аят'],
                ],
                'resize_keyboard': True,
            }),
        }),
    )
    assert unquote(got[1].url) == unquote(
        furl('https://some.domain/sendMessage')
        .add({
            'parse_mode': 'html',
            'text': '\n'.join([
                '<a href="https://umma.ru/link-to-sura#1-1">1:1-7)</a>',
                'Arab text\n',
                'Content\n',
                '<i>Transliteration</i>',
            ]),
            'chat_id': 321,
            'reply_markup': ujson.dumps({
                'keyboard': [
                    ['🎧 Подкасты'],
                    ['🕋 Время намаза', '🏘️ Поменять город'],
                    ['🌟 Избранное', '🔍 Найти аят'],
                ],
                'resize_keyboard': True,
            }),
        }),
    )


@pytest.mark.usefixtures('db_ayat', '_existed_user', '_admin_message')
async def test_exists_user(pgsql, fake_redis, unquote, settings_ctor):
    got = await FullStartAnswer(
        pgsql, FkAnswer(), FkSink(), fake_redis, settings_ctor(), FkLogSink(),
    ).build(FkUpdate('{"message":{"text":"/start"},"chat":{"id":321},"date":0}'))

    assert len(got) == 1
    assert unquote(got[0].url) == unquote(
        furl('https://some.domain/sendMessage')
        .add({
            'chat_id': 321,
            'text': 'Вы уже зарегистрированы!',
            'reply_markup': ujson.dumps({
                'keyboard': [
                    ['🎧 Подкасты'],
                    ['🕋 Время намаза', '🏘️ Поменять город'],
                    ['🌟 Избранное', '🔍 Найти аят'],
                ],
                'resize_keyboard': True,
            }),
        }),
    )


@pytest.mark.usefixtures('db_ayat', '_existed_user', '_admin_message')
async def test_with_referrer(pgsql, fake_redis, unquote, settings_ctor):
    got = await FullStartAnswer(
        pgsql, FkAnswer(), FkSink(), fake_redis, settings_ctor(), FkLogSink(),
    ).build(FkUpdate('{"message":{"text":"/start 1"},"chat":{"id":1},"date":1670581213}'))

    assert len(got) == 4
    assert unquote(got[0].url) == unquote(
        furl('https://some.domain/sendMessage')
        .add({
            'parse_mode': 'html',
            'text': 'start admin message',
            'chat_id': 1,
            'reply_markup': ujson.dumps({
                'keyboard': [
                    ['🎧 Подкасты'],
                    ['🕋 Время намаза', '🏘️ Поменять город'],
                    ['🌟 Избранное', '🔍 Найти аят'],
                ],
                'resize_keyboard': True,
            }),
        }),
    )
    assert unquote(got[2].url) == unquote(
        furl('https://some.domain/sendMessage')
        .add({
            'parse_mode': 'html',
            'text': 'По вашей реферальной ссылке произошла регистрация',
            'chat_id': 321,
            'reply_markup': ujson.dumps({
                'keyboard': [
                    ['🎧 Подкасты'],
                    ['🕋 Время намаза', '🏘️ Поменять город'],
                    ['🌟 Избранное', '🔍 Найти аят'],
                ],
                'resize_keyboard': True,
            }),
        }),
    )


@pytest.mark.usefixtures('db_ayat', '_existed_user', '_admin_message')
@pytest.mark.parametrize('referrer_id', [85, 3001])
async def test_fake_referrer(pgsql, fake_redis, referrer_id, settings_ctor):
    got = await FullStartAnswer(
        pgsql, FkAnswer(), FkSink(), fake_redis, settings_ctor(), FkLogSink(),
    ).build(FkUpdate(ujson.dumps({
        'message': {'text': '/start {0}'.format(referrer_id)},
        'chat': {'id': 1},
        'date': 0,
    })))

    assert len(got) == 3
