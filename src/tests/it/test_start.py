"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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

import pytest
from furl import furl

from app_types.logger import FkLogSink
from app_types.update import FkUpdate
from handlers.full_start_answer import FullStartAnswer
from integrations.tg.tg_answers import FkAnswer
from srv.events.sink import FkSink
from tests.unit.settings.test_amdin_chat_ids import FkSettings


@pytest.fixture()
async def _db_ayat(pgsql):
    created_at = datetime.datetime.now()
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        [
            {'file_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90', 'created_at': created_at},
            {'file_id': '99cce289-cfa0-4f92-8c3b-84aac82814ba', 'created_at': created_at},
        ],
    )
    await pgsql.execute(
        "INSERT INTO suras (sura_id, link)\nVALUES (1, '/link-to-sura.domain')",
    )
    await pgsql.execute(
        "INSERT INTO admin_messages (key, text)\nVALUES ('start', 'start admin message')",
    )
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO ayats',
            '(ayat_id, sura_id, public_id, day, audio_id, ayat_number, content, arab_text, transliteration)',
            'VALUES',
            '(:ayat_id, :sura_id, :public_id, :day, :audio_id, :ayat_number, :content, :arab_text, :transliteration)',
        ]),
        {
            'ayat_id': 1,
            'sura_id': 1,
            'public_id': '3067bdc4-8dc0-456b-aa68-e38122b5f2f8',
            'day': 1,
            'audio_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90',
            'ayat_number': '1-7',
            'content': 'Ayat content',
            'arab_text': 'Arab text',
            'transliteration': 'Transliteration',
        },
    )


@pytest.fixture()
async def _existed_user(pgsql):
    await pgsql.execute(
        'INSERT INTO users (chat_id, day, legacy_id) VALUES (321, 2, 1)',
    )


async def test(pgsql, rds, _db_ayat, unquote):
    got = await FullStartAnswer(
        pgsql, FkAnswer(), FkSink(), rds, FkSettings(), FkLogSink(),
    ).build(FkUpdate('{"message":{"text":"/start"},"chat":{"id":321}}'))

    assert len(got) == 3
    assert unquote(got[0].url) == unquote(
        furl('https://some.domain/sendMessage')
        .add({
            'parse_mode': 'html',
            'text': 'start admin message',
            'chat_id': 321,
            'reply_markup': json.dumps({
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
                '<a href="https://umma.ru/link-to-sura.domain#1-1">1:1-7)</a>',
                'Arab text\n',
                'Ayat content\n',
                '<i>Transliteration</i>',
            ]),
            'chat_id': 321,
            'reply_markup': json.dumps({
                'keyboard': [
                    ['🎧 Подкасты'],
                    ['🕋 Время намаза', '🏘️ Поменять город'],
                    ['🌟 Избранное', '🔍 Найти аят'],
                ],
                'resize_keyboard': True,
            }),
        }),
    )


@pytest.mark.usefixtures('_db_ayat', '_existed_user')
async def test_exists_user(pgsql, rds, unquote):
    got = await FullStartAnswer(
        pgsql, FkAnswer(), FkSink(), rds, FkSettings(), FkLogSink(),
    ).build(FkUpdate('{"message":{"text":"/start"},"chat":{"id":321},"date":0}'))

    assert len(got) == 1
    assert unquote(got[0].url) == unquote(
        furl('https://some.domain/sendMessage')
        .add({
            'chat_id': 321,
            'text': 'Вы уже зарегистрированы!',
            'reply_markup': json.dumps({
                'keyboard': [
                    ['🎧 Подкасты'],
                    ['🕋 Время намаза', '🏘️ Поменять город'],
                    ['🌟 Избранное', '🔍 Найти аят'],
                ],
                'resize_keyboard': True,
            }),
        }),
    )


@pytest.mark.usefixtures('_db_ayat', '_existed_user')
async def test_with_referrer(pgsql, rds, unquote):
    got = await FullStartAnswer(
        pgsql, FkAnswer(), FkSink(), rds, FkSettings(), FkLogSink(),
    ).build(FkUpdate('{"message":{"text":"/start 1"},"chat":{"id":1}}'))

    assert len(got) == 4
    assert unquote(got[0].url) == unquote(
        furl('https://some.domain/sendMessage')
        .add({
            'parse_mode': 'html',
            'text': 'start admin message',
            'chat_id': 1,
            'reply_markup': json.dumps({
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
            'reply_markup': json.dumps({
                'keyboard': [
                    ['🎧 Подкасты'],
                    ['🕋 Время намаза', '🏘️ Поменять город'],
                    ['🌟 Избранное', '🔍 Найти аят'],
                ],
                'resize_keyboard': True,
            }),
        }),
    )


@pytest.mark.usefixtures('_db_ayat', '_existed_user')
@pytest.mark.parametrize('referrer_id', [85, 3001])
async def test_fake_referrer(pgsql, rds, unquote, referrer_id):
    got = await FullStartAnswer(
        pgsql, FkAnswer(), FkSink(), rds, FkSettings(), FkLogSink(),
    ).build(FkUpdate(json.dumps({
        'message': {'text': '/start {0}'.format(referrer_id)},
        'chat': {'id': 1},
    })))

    assert len(got) == 3
