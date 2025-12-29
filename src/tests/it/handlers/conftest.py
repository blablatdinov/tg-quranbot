# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from pathlib import Path

import pytest
import pytz


@pytest.fixture
async def _prayers_from_csv(pgsql, city_factory, user_factory) -> None:
    lines = [
        line.split(';')
        for line in Path('src/tests/fixtures/prayers.csv').read_text(encoding='utf-8').splitlines()  # noqa: ASYNC240
    ]
    city = await city_factory('bc932b25-707e-4af1-8b6e-facb5e6dfa9b', 'Казань')
    await user_factory(358610865, city=city)
    query = '\n'.join([
        'INSERT INTO prayers (prayer_id, name, time, city_id, day)',
        'VALUES',
        '(:prayer_id, :name, :time, :city_id, :day)',
    ])
    await pgsql.execute_many(
        query,
        [
            {
                'prayer_id': int(line[0]),
                'name': line[1],
                'time': datetime.datetime.strptime(line[2], '%H:%M:%S').astimezone(
                    pytz.timezone('Europe/Moscow'),
                ),
                'city_id': line[3],
                'day': datetime.datetime.strptime(line[4], '%Y-%m-%d').astimezone(
                    pytz.timezone('Europe/Moscow'),
                ),
            }
            for line in lines
        ],
    )
    lines = [
        line.split(';')
        for line in Path(  # noqa: ASYNC240
            'src/tests/fixtures/prayers_at_user.csv',
        ).read_text(encoding='utf-8').splitlines()
    ]
    query = '\n'.join([
        'INSERT INTO prayers_at_user (prayer_at_user_id, user_id, prayer_id, is_read)',
        'VALUES',
        '(:prayer_at_user_id, 358610865, :prayer_id, :is_read)',
    ])
    await pgsql.execute_many(
        query,
        [
            {
                'prayer_at_user_id': int(line[0]),
                'prayer_id': int(line[3]),
                'is_read': line[4] == 'true',
            }
            for line in lines
        ],
    )
