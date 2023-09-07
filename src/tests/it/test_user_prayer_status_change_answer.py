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
import json

import pytest

from app_types.update import FkUpdate
from handlers.user_prayer_status_change_answer import UserPrayerStatusChangeAnswer
from integrations.tg.tg_answers import FkAnswer
from repository.prayer_time import UserPrayers
from services.prayers.prayer_status import UserPrayerStatus


@pytest.fixture()
async def generated_prayers(pgsql):
    query = """
        INSERT INTO cities (city_id, name) VALUES ('080fd3f4-678e-4a1c-97d2-4460700fe7ac', 'Kazan')
    """
    await pgsql.execute(query)
    query = """
        INSERT INTO users (chat_id, city_id) VALUES (905, '080fd3f4-678e-4a1c-97d2-4460700fe7ac')
    """
    await pgsql.execute(query)
    query = """
        INSERT INTO prayers (prayer_id, name, "time", city_id, day) VALUES
        (1, 'fajr', '05:43:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),
        (2, 'sunrise', '08:02:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),
        (3, 'dhuhr', '12:00:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),
        (4, 'asr', '13:21:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),
        (5, 'maghrib', '15:07:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),
        (6, 'isha''a', '17:04:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19')
    """
    await pgsql.execute(query)
    query = """
        INSERT INTO prayers_at_user (user_id, prayer_id, is_read) VALUES
        (905, 1, false),
        (905, 2, false),
        (905, 3, false),
        (905, 4, false),
        (905, 5, false),
        (905, 6, false)
    """
    await pgsql.execute(query)


async def test_before(pgsql, rds, generated_prayers, freezer):
    freezer.move_to('2023-09-07')
    got = await UserPrayerStatusChangeAnswer(
        FkAnswer(),
        UserPrayerStatus(pgsql),
        UserPrayers(pgsql),
        pgsql,
    ).build(
        FkUpdate('{"callback_query": {"data": "mark_readed(3)"}, "message": {"message_id": 17}, "chat": {"id": 905}}'),
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
    assert got[0].url.path == '/'
