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
import datetime
from pathlib import Path

import pytest

from integrations.tg.chat_id import FkChatId
from srv.prayers.prayers_statistic import PgPrayersStatisic


@pytest.fixture()
async def _prayers(pgsql):
    lines = [
        line.split(';')
        for line in
        Path('src/tests/fixtures/prayers.csv').read_text().splitlines()
    ]
    await pgsql.execute("INSERT INTO cities (city_id, name) VALUES ('bc932b25-707e-4af1-8b6e-facb5e6dfa9b', 'Казань')")
    await pgsql.execute(
        "INSERT INTO users (chat_id, city_id) VALUES (358610865, 'bc932b25-707e-4af1-8b6e-facb5e6dfa9b')",
    )
    query = """
        INSERT INTO prayers (prayer_id, name, time, city_id, day)
        VALUES
        (:prayer_id, :name, :time, :city_id, :day)
    """
    await pgsql.execute_many(
        query,
        [
            {
                'prayer_id': int(line[0]),
                'name': line[1],
                'time': datetime.datetime.strptime(line[2], '%H:%M:%S'),
                'city_id': line[3],
                'day': datetime.datetime.strptime(line[4], '%Y-%m-%d'),
            }
            for line in lines
        ]
    )
    lines = [
        line.split(';')
        for line in
        Path('src/tests/fixtures/prayers_at_user.csv').read_text().splitlines()
    ]
    query = """
        INSERT INTO prayers_at_user (prayer_at_user_id, user_id, prayer_id, is_read)
        VALUES
        (:prayer_at_user_id, 358610865, :prayer_id, :is_read)
    """
    await pgsql.execute_many(
        query,
        [
            {
                'prayer_at_user_id': int(line[0]),
                'prayer_id': int(line[3]),
                'is_read': line[4] == 'true',
            }
            for line in lines
        ]
    )


@pytest.mark.usefixtures('_prayers')
async def test(pgsql):
    got = await PgPrayersStatisic(pgsql, FkChatId(358610865)).csv()

    assert got == '\n'.join([
        "Day;fajr;dhuhr;asr;maghrib;isha'a",
        '2023-10-01;False;False;False;False;False',
        '2023-10-02;False;False;False;False;False',
        '2023-10-04;False;True;True;False;False',
        '2023-10-05;False;False;False;False;False',
        '2023-10-06;False;False;False;False;False',
        '2023-10-10;True;True;True;True;True',
        '2023-10-11;True;True;True;True;True',
        '2023-10-12;True;True;True;True;False',
        '2023-10-13;True;True;True;True;True',
        '2023-10-14;True;True;True;True;False',
        '2023-10-15;True;True;True;True;False',
        '2023-10-16;True;True;True;True;False',
        '2023-10-17;False;True;True;True;True',
        '2023-10-18;True;True;True;True;True',
        '2023-10-19;True;True;True;True;True',
        '2023-10-20;True;False;False;True;True',
        '2023-10-21;False;False;False;True;True',
        '2023-10-22;False;True;True;False;True',
        '2023-10-23;True;False;False;False;True',
        '2023-10-25;True;True;False;True;False',
        '2023-10-26;False;False;False;False;True',
        '2023-10-27;False;False;False;False;False',
        '2023-11-01;False;False;False;False;True',
    ])
