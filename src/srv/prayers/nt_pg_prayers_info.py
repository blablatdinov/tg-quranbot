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

import attrs
import pytz
from asyncpg.exceptions import UniqueViolationError
from databases import Database

from exceptions.prayer_exceptions import PrayersAlreadyExistsError
from srv.prayers.pg_city import PgCity
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
@attrs.define(frozen=True)
class NtPgPrayersInfo(PrayersInfo):
    """Декоратор для создания записи о времени намаза в таблице prayers."""

    _origin: PrayersInfo
    _pgsql: Database

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
        origin = await self._origin.to_dict()
        city_id = await PgCity.name_ctor(origin['city_name'], self._pgsql).city_id()
        day = (
            datetime.datetime
            .strptime(origin['date'], '%d.%m.%Y')
            .replace(tzinfo=pytz.timezone('Europe/Moscow'))
            .date()
        )
        try:
            await self._pgsql.execute_many(
                '\n'.join([
                    'INSERT INTO prayers (name, time, city_id, day)',
                    'VALUES',
                    '(:name, :time, :city_id, :day)',
                ]),
                [
                    {
                        'name': prayer_name,
                        'time': datetime.datetime.strptime(
                            # Keys are checked in the loop
                            origin[key], '%H:%M',  # type: ignore [literal-required]
                        ).replace(tzinfo=pytz.timezone('Europe/Moscow')).time(),
                        'city_id': city_id,
                        'day': day,
                    }
                    for prayer_name, key in zip(
                        [
                            'fajr',
                            'sunrise',
                            'dhuhr',
                            'asr',
                            'maghrib',
                            "isha'a",
                        ],
                        [
                            'fajr_prayer_time',
                            'sunrise_prayer_time',
                            'dhuhr_prayer_time',
                            'asr_prayer_time',
                            'magrib_prayer_time',
                            'ishaa_prayer_time',
                        ],
                        strict=True,
                    )
                ],
            )
        except UniqueViolationError as err:
            raise PrayersAlreadyExistsError from err
        return origin
