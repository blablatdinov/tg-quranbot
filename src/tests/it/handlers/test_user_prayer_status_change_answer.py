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
import pytz

from app_types.logger import FkLogSink
from app_types.stringable import FkAsyncStr
from app_types.update import FkUpdate
from handlers.prayer_time_answer import PrayerTimeAnswer
from handlers.user_prayer_status_change_answer import UserPrayerStatusChangeAnswer
from integrations.tg.tg_answers import FkAnswer
from settings.settings import FkSettings
from srv.prayers.prayer_date import FkPrayerDate
from srv.prayers.prayers_text import PrayersText


@pytest.fixture()
async def _prayers(pgsql):
    await pgsql.execute("INSERT INTO cities (city_id, name) VALUES ('080fd3f4-678e-4a1c-97d2-4460700fe7ac', 'Kazan')")
    await pgsql.execute("INSERT INTO users (chat_id, city_id) VALUES (905, '080fd3f4-678e-4a1c-97d2-4460700fe7ac')")
    query = '\n'.join([
        'INSERT INTO prayers (prayer_id, name, "time", city_id, day) VALUES',
        "(1, 'fajr', '05:43:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(2, 'sunrise', '08:02:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(3, 'dhuhr', '12:00:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(4, 'asr', '13:21:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(5, 'maghrib', '15:07:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(6, 'isha''a', '17:04:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19')",
    ])
    await pgsql.execute(query)


@pytest.fixture()
async def _generated_prayers(pgsql, _prayers):
    query = '\n'.join([
        'INSERT INTO prayers_at_user (user_id, prayer_id, is_read) VALUES',
        '(905, 1, false),',
        '(905, 2, false),',
        '(905, 3, false),',
        '(905, 4, false),',
        '(905, 5, false),',
        '(905, 6, false)',
    ])
    await pgsql.execute(query)


@pytest.mark.usefixtures('_prayers')
async def test_new_prayer_times(pgsql, fake_redis, time_machine):
    time_machine.move_to('2023-12-19')
    got = await PrayerTimeAnswer.new_prayers_ctor(
        pgsql, FkAnswer(), [123], fake_redis, FkLogSink(), FkSettings({'RAMADAN_MODE': 'off'}),
    ).build(
        FkUpdate(json.dumps({
            'callback_query': {'data': 'mark_readed(3)'},
            'message': {'message_id': 17, 'text': 'Время намаза'},
            'chat': {'id': 905},
        })),
    )

    assert json.loads(got[0].url.params.get('reply_markup')) == {
        'inline_keyboard': [
            [
                {'callback_data': 'mark_readed(1)', 'text': '❌'},
                {'callback_data': 'mark_readed(2)', 'text': '❌'},
                {'callback_data': 'mark_readed(3)', 'text': '❌'},
                {'callback_data': 'mark_readed(4)', 'text': '❌'},
                {'callback_data': 'mark_readed(5)', 'text': '❌'},
            ],
        ],
    }
    assert got[0].url.path == '/sendMessage'


@pytest.mark.usefixtures('_generated_prayers')
async def test_today(pgsql, fake_redis, time_machine):
    time_machine.move_to('2023-12-19')
    got = await UserPrayerStatusChangeAnswer(
        FkAnswer(), pgsql, fake_redis, FkLogSink(), FkSettings({'RAMADAN_MODE': 'off'}),
    ).build(
        FkUpdate(json.dumps({
            'callback_query': {'data': 'mark_readed(3)'},
            'message': {
                'message_id': 17,
                'text': '\n'.join([
                    'Время намаза для г. Казань (19.12.2023)\n',
                    'Иртәнге: 04:02',
                    'Восход: 06:05',
                    'Өйлә: 12:00',
                    'Икенде: 14:57',
                    'Ахшам: 16:55',
                    'Ястү: 18:36',
                ]),
            },
            'chat': {'id': 905},
        })),
    )

    assert json.loads(got[0].url.params.get('reply_markup')) == {
        'inline_keyboard': [
            [
                {'callback_data': 'mark_readed(1)', 'text': '❌'},
                {'callback_data': 'mark_not_readed(3)', 'text': '✅'},
                {'callback_data': 'mark_readed(4)', 'text': '❌'},
                {'callback_data': 'mark_readed(5)', 'text': '❌'},
                {'callback_data': 'mark_readed(6)', 'text': '❌'},
            ],
        ],
    }
    assert got[0].url.path == '/editMessageReplyMarkup'


@pytest.mark.usefixtures('_generated_prayers')
async def test_before(pgsql, fake_redis, time_machine, unquote):
    time_machine.move_to('2023-12-19')
    got = await UserPrayerStatusChangeAnswer(
        FkAnswer(), pgsql, fake_redis, FkLogSink(), FkSettings({'RAMADAN_MODE': 'off'}),
    ).build(
        FkUpdate(json.dumps({
            'callback_query': {'data': 'mark_readed(3)'},
            'message': {
                'message_id': 17,
                'text': '\n'.join([
                    'Время намаза для г. Казань (19.12.2023)\n',
                    'Иртәнге: 04:02',
                    'Восход: 06:05',
                    'Өйлә: 12:00',
                    'Икенде: 14:57',
                    'Ахшам: 16:55',
                    'Ястү: 18:36',
                ]),
            },
            'chat': {'id': 905},
        })),
    )

    assert json.loads(got[0].url.params.get('reply_markup')) == {
        'inline_keyboard': [
            [
                {'callback_data': 'mark_readed(1)', 'text': '❌'},
                {'callback_data': 'mark_not_readed(3)', 'text': '✅'},
                {'callback_data': 'mark_readed(4)', 'text': '❌'},
                {'callback_data': 'mark_readed(5)', 'text': '❌'},
                {'callback_data': 'mark_readed(6)', 'text': '❌'},
            ],
        ],
    }
    assert got[0].url.path == '/editMessageReplyMarkup'


@pytest.mark.usefixtures('_generated_prayers')
async def test_prayers_text(pgsql):
    got = await PrayersText(
        pgsql,
        FkPrayerDate(datetime.datetime(2023, 12, 19, tzinfo=pytz.timezone('Europe/Moscow'))),
        FkAsyncStr('080fd3f4-678e-4a1c-97d2-4460700fe7ac'),
        FkUpdate('{"message":{"text":"Время намаза"}}'),
    ).to_str()

    assert got == '\n'.join([
        'Время намаза для г. Kazan (19.12.2023)\n',
        'Иртәнге: 05:43',
        'Восход: 08:02',
        'Өйлә: 12:00',
        'Икенде: 13:21',
        'Ахшам: 15:07',
        'Ястү: 17:04',
    ])


@pytest.mark.usefixtures('_generated_prayers')
async def test_without_message_text(pgsql, fake_redis):
    """Случай без текста в update.

    Почему-то телеграм не присылает текст сообщения спустя время
    """
    got = await UserPrayerStatusChangeAnswer(
        FkAnswer(), pgsql, fake_redis, FkLogSink(), FkSettings({'RAMADAN_MODE': 'off'}),
    ).build(
        FkUpdate(json.dumps({
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
    assert got[0].url.params['text'] == '\n'.join([
        'Время намаза для г. Kazan (19.12.2023)\n',
        'Иртәнге: 05:43',
        'Восход: 08:02',
        'Өйлә: 12:00',
        'Икенде: 13:21',
        'Ахшам: 15:07',
        'Ястү: 17:04',
    ])
    assert json.loads(got[0].url.params['reply_markup']) == {
        'inline_keyboard': [
            [
                {'callback_data': 'mark_readed(1)', 'text': '❌'},
                {'callback_data': 'mark_readed(3)', 'text': '❌'},
                {'callback_data': 'mark_readed(4)', 'text': '❌'},
                {'callback_data': 'mark_not_readed(5)', 'text': '✅'},
                {'callback_data': 'mark_readed(6)', 'text': '❌'},
            ],
        ],
    }
