# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

from app_types.fk_log_sink import FkLogSink
from srv.prayers.cd_prayers_info import CdPrayersInfo
from srv.prayers.fk_city import FkCity
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
class _FkPrayersInfo(PrayersInfo):  # noqa: PEO200. Object for test only

    def __init__(self) -> None:
        self._flag = False

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        if self._flag:
            raise ValueError
        self._flag = True
        return {
            'asr_prayer_time': '14:02',
            'city_name': 'Казань',
            'date': '20.01.2025',
            'dhuhr_prayer_time': '11:56',
            'fajr_prayer_time': '05:44',
            'ishaa_prayer_time': '17:44',
            'magrib_prayer_time': '15:53',
            'sunrise_prayer_time': '07:57',
        }


async def test(fake_redis):
    cd_prayer_info = CdPrayersInfo(
        _FkPrayersInfo(),
        fake_redis,
        FkCity.name_ctor('kazan'),
        FkPrayerDate(datetime.date(2025, 1, 6)),
        FkLogSink(),
    )
    await cd_prayer_info.to_dict()
    got = await cd_prayer_info.to_dict()

    assert got == {
        'asr_prayer_time': '14:02',
        'city_name': 'Казань',
        'date': '20.01.2025',
        'dhuhr_prayer_time': '11:56',
        'fajr_prayer_time': '05:44',
        'ishaa_prayer_time': '17:44',
        'magrib_prayer_time': '15:53',
        'sunrise_prayer_time': '07:57',
    }
    assert await fake_redis.keys() == [b'prayers:kazan:2025-01-06']
