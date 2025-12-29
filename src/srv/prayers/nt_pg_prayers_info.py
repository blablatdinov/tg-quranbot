# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
