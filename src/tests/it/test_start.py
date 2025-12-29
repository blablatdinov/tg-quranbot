# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
import ujson
from furl import furl

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from handlers.full_start_answer import FullStartAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.events.fk_sink import FkSink


@pytest.fixture
async def _existed_user(user_factory):
    await user_factory(321, 2, city=None, legacy_id=1)


@pytest.fixture
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
