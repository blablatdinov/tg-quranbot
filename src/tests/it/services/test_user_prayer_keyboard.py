# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import asyncio
import datetime
from itertools import chain, repeat

import pytest

from app_types.fk_update import FkUpdate
from exceptions.prayer_exceptions import PrayersNotFoundError
from services.user_prayer_keyboard import UserPrayersKeyboard
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.pg_updated_user_city import PgUpdatedUserCity
from srv.prayers.prayer_names import PrayerNames


@pytest.fixture
async def cities(city_factory):
    return (
        await city_factory('e22d9142-a39b-4e99-92f7-2082766f0987', 'Kazan'),
        await city_factory('4bd2af2a-aec9-4660-b710-405940f6e578', 'NabChelny'),
    )


@pytest.fixture
async def user(cities, user_factory):
    return await user_factory(849375, 2, city=cities[0])


@pytest.fixture
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


@pytest.fixture
async def user_with_changed_city(user, pgsql, cities):
    await UserPrayersKeyboard(
        pgsql,
        FkPrayerDate(datetime.date(2024, 6, 5)),
        await user.chat_id(),
    ).generate(FkUpdate.empty_ctor())
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
        ).generate(FkUpdate.empty_ctor())
        for _ in range(10)
    ]
    await asyncio.gather(*tasks)

    assert len(await pgsql.fetch_all('SELECT * FROM prayers_at_user')) == 5


async def test_empty(pgsql, user):
    with pytest.raises(PrayersNotFoundError):
        await UserPrayersKeyboard(
            pgsql,
            FkPrayerDate(datetime.date(2024, 6, 5)),
            await user.chat_id(),
        ).generate(FkUpdate.empty_ctor())


@pytest.mark.usefixtures('_prayers')
async def test_change_city(pgsql, user_with_changed_city):
    await UserPrayersKeyboard(
        pgsql,
        FkPrayerDate(datetime.date(2024, 6, 5)),
        await user_with_changed_city.chat_id(),
    ).generate(FkUpdate.empty_ctor())

    assert await pgsql.fetch_val('SELECT COUNT(*) FROM prayers_at_user') == 5
