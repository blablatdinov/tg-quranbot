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

import asyncio
import datetime
import uuid
from itertools import chain, repeat

import pytest

from app_types.FkUpdate import FkUpdate
from exceptions.internal_exceptions import PrayerAtUserNotCreatedError
from handlers.PrayerNames import PrayerNames
from services.user_prayer_keyboard import UserPrayersKeyboard
from srv.prayers.fk_city import FkCity
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.pg_updated_user_city import PgUpdatedUserCity
from srv.users.pg_user import PgUser


@pytest.fixture()
async def cities(pgsql):
    await pgsql.execute_many(
        'INSERT INTO cities (city_id, name) VALUES (:city_id, :name)',
        [
            {'city_id': city_id, 'name': city_name}
            for city_id, city_name in (
                ('e22d9142-a39b-4e99-92f7-2082766f0987', 'Kazan'),
                ('4bd2af2a-aec9-4660-b710-405940f6e578', 'NabChelny'),
            )
        ],
    )
    return (
        FkCity(
            uuid.UUID('e22d9142-a39b-4e99-92f7-2082766f0987'),
            'Kazan',
        ),
        FkCity(
            uuid.UUID('4bd2af2a-aec9-4660-b710-405940f6e578'),
            'NabChelny',
        ),
    )


@pytest.fixture()
async def user(pgsql, cities):
    await pgsql.execute(
        'INSERT INTO users (chat_id, is_active, day, city_id) VALUES (:chat_id, :is_active, :day, :city_id)',
        {'chat_id': 849375, 'is_active': True, 'day': 2, 'city_id': await cities[0].city_id()},
    )
    return PgUser.int_ctor(849375, pgsql)


@pytest.fixture()
async def _prayers(pgsql, cities):
    prayer_times = [
        datetime.time(hour, 30)
        for hour in range(4, 10)
    ]
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO prayers (prayer_id, name, time, city_id, day)',
            'VALUES (:prayer_id, :prayer_name, :time, :city_id, :day)',
        ]),
        [
            {
                'prayer_id': pr_id,
                'prayer_name': pr_name,
                'time': pr_time,
                'city_id': await city.city_id(),
                'day': datetime.date(2024, 6, 5),
            }
            for pr_id, pr_name, pr_time, city in zip(
                range(1, 13),
                chain.from_iterable(repeat(
                    [field.value[0] for field in PrayerNames],
                    2,
                )),
                chain.from_iterable(repeat(prayer_times, 2)),
                chain(repeat(cities[0], 6), repeat(cities[1], 6)),
                strict=True,
            )
        ],
    )


@pytest.fixture()
async def user_with_changed_city(user, pgsql, cities):
    await UserPrayersKeyboard(
        pgsql,
        FkPrayerDate(datetime.date(2024, 6, 5)),
        await user.chat_id(),
    ).generate(FkUpdate())
    await PgUpdatedUserCity(
        cities[1],
        await user.chat_id(),
        pgsql,
    ).update()
    return user


@pytest.mark.parametrize('execution_number', range(10))
@pytest.mark.usefixtures('_prayers')
async def test(pgsql, user, execution_number):
    tasks = [
        UserPrayersKeyboard(
            pgsql,
            FkPrayerDate(datetime.date(2024, 6, 5)),
            await user.chat_id(),
        ).generate(FkUpdate())
        for _ in range(10)
    ]
    await asyncio.gather(*tasks)

    assert len(await pgsql.fetch_all('SELECT * FROM prayers_at_user')) == 5


async def test_empty(pgsql, user):
    with pytest.raises(PrayerAtUserNotCreatedError):
        await UserPrayersKeyboard(
            pgsql,
            FkPrayerDate(datetime.date(2024, 6, 5)),
            await user.chat_id(),
        ).generate(FkUpdate())


@pytest.mark.usefixtures('_prayers')
async def test_change_city(pgsql, user_with_changed_city):
    await UserPrayersKeyboard(
        pgsql,
        FkPrayerDate(datetime.date(2024, 6, 5)),
        await user_with_changed_city.chat_id(),
    ).generate(FkUpdate())

    assert await pgsql.fetch_val('SELECT COUNT(*) FROM prayers_at_user') == 5
