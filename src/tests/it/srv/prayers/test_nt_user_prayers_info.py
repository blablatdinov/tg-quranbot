# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid

import pytest

from integrations.tg.fk_chat_id import FkChatId
from srv.prayers.fk_city import FkCity
from srv.prayers.fk_prayers_info import FkPrayersInfo
from srv.prayers.nt_pg_prayers_info import NtPgPrayersInfo
from srv.prayers.nt_user_prayers_info import NtUserPrayersInfo


@pytest.fixture
async def _db_city(city_factory):
    await city_factory('e9fa0fff-4e6a-47c8-8654-09adf913734a', 'Казань')


@pytest.fixture
async def _user(user_factory):
    await user_factory(1, city=FkCity(uuid.UUID('e9fa0fff-4e6a-47c8-8654-09adf913734a'), 'Казань'))


@pytest.fixture
async def _prayers(pgsql):
    await NtPgPrayersInfo(
        FkPrayersInfo({
            'city_name': 'Казань',
            'date': '21.10.2023',
            'fajr_prayer_time': '04:22',
            'sunrise_prayer_time': '06:26',
            'dhuhr_prayer_time': '12:00',
            'asr_prayer_time': '14:35',
            'magrib_prayer_time': '16:30',
            'ishaa_prayer_time': '18:12',
        }),
        pgsql,
    ).to_dict()


@pytest.mark.usefixtures('_db_city', '_user', '_prayers')
async def test(pgsql):
    await NtUserPrayersInfo(
        FkPrayersInfo({
            'city_name': 'Казань',
            'date': '21.10.2023',
            'fajr_prayer_time': '04:22',
            'sunrise_prayer_time': '06:26',
            'dhuhr_prayer_time': '12:00',
            'asr_prayer_time': '14:35',
            'magrib_prayer_time': '16:30',
            'ishaa_prayer_time': '18:12',
        }),
        pgsql,
        FkChatId(1),
    ).to_dict()

    assert [
        dict(row)
        for row in await pgsql.fetch_all('select user_id, is_read from prayers_at_user')
    ] == [
        {
            'is_read': False,
            'user_id': 1,
        }
        for _ in range(5)
    ]


@pytest.mark.usefixtures('_db_city', '_user', '_prayers')
async def test_double(pgsql):
    nt_user_prayers_info = NtUserPrayersInfo(
        FkPrayersInfo({
            'city_name': 'Казань',
            'date': '21.10.2023',
            'fajr_prayer_time': '04:22',
            'sunrise_prayer_time': '06:26',
            'dhuhr_prayer_time': '12:00',
            'asr_prayer_time': '14:35',
            'magrib_prayer_time': '16:30',
            'ishaa_prayer_time': '18:12',
        }),
        pgsql,
        FkChatId(1),
    )
    await nt_user_prayers_info.to_dict()
    await nt_user_prayers_info.to_dict()

    assert await pgsql.fetch_val('select count(*) from prayers_at_user') == 5
