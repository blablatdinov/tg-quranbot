# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Final, final, override

import attrs
from databases import Database

from app_types.async_supports_str import AsyncSupportsStr
from app_types.update import Update
from exceptions.prayer_exceptions import PrayersNotFoundError
from integrations.city_name_by_id import CityNameById
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo

TIME_LITERAL: Final = 'time'


@final
@attrs.define(frozen=True)
class PgPrayersInfo(PrayersInfo):
    """Информация о времени намаза из БД."""

    _pgsql: Database
    _date: PrayerDate
    _city_id: AsyncSupportsStr
    _update: Update

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
        query = '\n'.join([
            'SELECT',
            '    c.name AS city_name,',
            '    p.day,',
            '    p.time,',
            '    p.name',
            'FROM prayers AS p',
            'INNER JOIN cities AS c ON p.city_id = c.city_id',
            'WHERE p.day = :date AND c.city_id = :city_id',
            'ORDER BY',
            "    ARRAY_POSITION(ARRAY['fajr', 'sunrise', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
        ])
        rows = await self._pgsql.fetch_all(query, {
            'date': await self._date.parse(self._update),
            'city_id': await self._city_id.to_str(),
        })
        if not rows:
            raise PrayersNotFoundError(
                await CityNameById(self._pgsql, self._city_id).to_str(),
                await self._date.parse(self._update),
            )
        time_format = '%H:%M'
        return PrayerMessageTextDict({
            'city_name': rows[0]['city_name'],
            'date': rows[0]['day'].strftime('%d.%m.%Y'),
            'fajr_prayer_time': rows[0][TIME_LITERAL].strftime(time_format),
            'sunrise_prayer_time': rows[1][TIME_LITERAL].strftime(time_format),
            'dhuhr_prayer_time': rows[2][TIME_LITERAL].strftime(time_format),
            'asr_prayer_time': rows[3][TIME_LITERAL].strftime(time_format),
            'magrib_prayer_time': rows[4][TIME_LITERAL].strftime(time_format),
            'ishaa_prayer_time': rows[5][TIME_LITERAL].strftime(time_format),
        })
