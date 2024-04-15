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

import urllib
import uuid

import pytest

from app_types.logger import FkLogSink
from app_types.update import FkUpdate
from handlers.prayer_time_answer import PrayerTimeAnswer
from integrations.tg.tg_answers import FkAnswer


@pytest.fixture()
async def _user(pgsql):
    city_id = str(uuid.uuid4())
    await pgsql.execute("INSERT INTO cities (city_id, name) VALUES (:city_id, 'Казань')", {'city_id': city_id})
    await pgsql.execute(
        'INSERT INTO users (chat_id, city_id) VALUES (:chat_id, :city_id)',
        {'chat_id': 123, 'city_id': city_id},
    )


@pytest.mark.usefixtures('_user')
async def test_not_found_prayer(pgsql, fake_redis, time_machine, settings_ctor):
    time_machine.move_to('2023-08-30')
    got = await PrayerTimeAnswer.new_prayers_ctor(
        pgsql,
        FkAnswer(),
        [321],
        fake_redis,
        FkLogSink(),
        settings_ctor(ramadan_mode=True),
    ).build(FkUpdate('{"chat":{"id":123},"message":{"message_id":1,"text":"Время намаза"}}'))

    assert len(got) == 2
    assert urllib.parse.unquote(
        str(got[0].url),
    ).replace('+', ' ') == ''.join([
        'https://some.domain/sendMessage',
        '?chat_id=123&text=Время намаза на 30.08.2023 для города Казань не найдено',
    ])
    assert urllib.parse.unquote(
        str(got[1].url),
    ).replace('+', ' ') == ''.join([
        'https://some.domain/sendMessage',
        '?chat_id=321&text=Время намаза на 30.08.2023 для города Казань не найдено',
    ])
