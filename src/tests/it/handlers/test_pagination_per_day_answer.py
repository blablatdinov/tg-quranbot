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

import pytest
import pytz
import ujson

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from handlers.pagination_per_day_prayer_answer import PaginationPerDayPrayerAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


@pytest.mark.parametrize('date', [
    datetime.datetime(2014, 2, 17, tzinfo=pytz.timezone('Europe/Moscow')).date(),
    datetime.datetime(2100, 2, 17, tzinfo=pytz.timezone('Europe/Moscow')).date(),
])
async def test_dates(
    callback_update_factory,
    pgsql,
    fake_redis,
    settings_ctor,
    prayers_factory,
    date,
):
    await prayers_factory(date)
    got = await PaginationPerDayPrayerAnswer(
        FkAnswer(),
        pgsql,
        [123],
        fake_redis,
        FkLogSink(),
        settings_ctor(),
    ).build(
        FkUpdate(
            callback_update_factory(
                chat_id=905, callback_data='pagPrDay({0})'.format(date.strftime('%Y-%m-%d')),
            ),
        ),
    )

    assert ujson.loads(
        got[0].url.params.get('reply_markup'),
    )['inline_keyboard'][1] == [
        {
            'callback_data': 'pagPrDay({0})'.format((date - datetime.timedelta(days=1)).strftime('%d.%m.%Y')),
            'text': '<- {0}'.format((date - datetime.timedelta(days=1)).strftime('%d.%m')),
        },
        {
            'callback_data': 'pagPrDay({0})'.format((date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')),
            'text': '{0} ->'.format((date + datetime.timedelta(days=1)).strftime('%d.%m')),
        },
    ]


async def test(
    callback_update_factory,
    pgsql,
    fake_redis,
    settings_ctor,
    prayers_factory,
):
    await prayers_factory('2024-09-02')
    got = await PaginationPerDayPrayerAnswer(
        FkAnswer(),
        pgsql,
        [123],
        fake_redis,
        FkLogSink(),
        settings_ctor(),
    ).build(
        FkUpdate(
            callback_update_factory(
                chat_id=905, callback_data='pagPrDay(2024-09-02)',
            ),
        ),
    )

    assert got[0].url.params.get('text') == '\n'.join([
        'Время намаза для г. Kazan (02.09.2024)',
        '',
        'Иртәнге: 05:43',
        'Восход: 08:02',
        'Өйлә: 12:00',
        'Икенде: 13:21',
        'Ахшам: 15:07',
        'Ястү: 17:04',
    ])
    assert ujson.loads(got[0].url.params.get('reply_markup')) == {
        'inline_keyboard': [
            [
                {'callback_data': 'mark_readed(1)', 'text': '❌'},
                {'callback_data': 'mark_readed(2)', 'text': '❌'},
                {'callback_data': 'mark_readed(3)', 'text': '❌'},
                {'callback_data': 'mark_readed(4)', 'text': '❌'},
                {'callback_data': 'mark_readed(5)', 'text': '❌'},
            ],
            [
                {'callback_data': 'pagPrDay(01.09.2024)', 'text': '<- 01.09'},
                {'callback_data': 'pagPrDay(03.09.2024)', 'text': '03.09 ->'},
            ],
        ],
    }
