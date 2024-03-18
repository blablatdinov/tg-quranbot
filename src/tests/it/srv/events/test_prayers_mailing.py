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

import httpx
import pytest
import ujson
from eljson.json_doc import JsonDoc
from furl import furl
from loguru import logger

from integrations.tg.tg_answers import TgEmptyAnswer
from settings.settings import FkSettings
from srv.events.prayers_mailing import PrayersMailingPublishedEvent
from srv.events.sink import RabbitmqSink
from srv.users.pg_user import PgUser


@pytest.fixture()
def _mock_http(respx_mock):
    rv = {
        'return_value': httpx.Response(
            200, text=ujson.dumps({'ok': True, 'result': True}),
        ),
    }
    chat_content = {
        '358610865': '\n'.join([
            'Время намаза для г. Kazan (07.03.2024)\n',
            'Иртәнге: 04:30',
            'Восход: 05:30',
            'Өйлә: 06:30',
            'Икенде: 07:30',
            'Ахшам: 08:30',
            'Ястү: 09:30',
        ]),
    }
    for chat_id, text in chat_content.items():
        respx_mock.get(str(furl('https://api.telegram.org/botfakeToken/sendMessage').add({
            'text': text,
            'chat_id': chat_id,
            'reply_markup': ujson.dumps({
                'inline_keyboard': [[
                    {'text': '\u274c', 'callback_data': 'mark_readed(1)'},
                    {'text': '\u274c', 'callback_data': 'mark_readed(2)'},
                    {'text': '\u274c', 'callback_data': 'mark_readed(3)'},
                    {'text': '\u274c', 'callback_data': 'mark_readed(4)'},
                    {'text': '\u274c', 'callback_data': 'mark_readed(5)'},
                ]],
            }),
            'parse_mode': 'html',
        }))).mock(**rv)


@pytest.fixture()
async def users(pgsql):
    await pgsql.execute_many(
        'INSERT INTO cities (city_id, name) VALUES (:city_id, :name)',
        [
            {'city_id': city_id, 'name': 'Kazan'}
            for city_id in ('e22d9142-a39b-4e99-92f7-2082766f0987',)
        ],
    )
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO prayers (prayer_id, name, time, city_id, day)',
            'VALUES (:prayer_id, :prayer_name, :time, :city_id, :day)',
        ]),
        [
            {
                'prayer_id': 1,
                'prayer_name': 'fajr',
                'time': datetime.time(4, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 3, 7),
            },
            {
                'prayer_id': 2,
                'prayer_name': 'sunrise',
                'time': datetime.time(5, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 3, 7),
            },
            {
                'prayer_id': 3,
                'prayer_name': 'dhuhr',
                'time': datetime.time(6, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 3, 7),
            },
            {
                'prayer_id': 4,
                'prayer_name': 'asr',
                'time': datetime.time(7, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 3, 7),
            },
            {
                'prayer_id': 5,
                'prayer_name': 'maghrib',
                'time': datetime.time(8, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 3, 7),
            },
            {
                'prayer_id': 6,
                'prayer_name': "isha'a",
                'time': datetime.time(9, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 3, 7),
            },
        ],
    )
    await pgsql.execute_many(
        "INSERT INTO users (chat_id, is_active, day, city_id) VALUES (:chat_id, 't', 2, :city_id)",
        [
            {'chat_id': 358610865, 'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987'},
        ],
    )
    return [
        PgUser.int_ctor(row['chat_id'], pgsql)
        for row in await pgsql.fetch_all('SELECT chat_id FROM users')
    ]


@pytest.mark.usefixtures('_mock_http')
async def test(pgsql, users, fake_redis, time_machine):
    time_machine.move_to('2024-03-06')
    settings = FkSettings(
        {
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASS': 'guest',
            'RABBITMQ_VHOST': '',
            'DAILY_PRAYERS': 'on',
            'ADMIN_CHAT_IDS': '358610865',
            'RAMADAN_MODE': 'off',
        },
    )
    await PrayersMailingPublishedEvent(
        TgEmptyAnswer('fakeToken'),
        pgsql,
        settings,
        RabbitmqSink(settings, logger),
        logger,
        fake_redis,
    ).process(JsonDoc({}))
