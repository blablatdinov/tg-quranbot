# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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
from typing import final, override


from srv.prayers.cd_prayers_info import CdPrayersInfo
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.prayers_info import PrayersInfo, PrayerMessageTextDict


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
        'kazan',
        FkPrayerDate(datetime.date(2025, 1, 6)),
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
