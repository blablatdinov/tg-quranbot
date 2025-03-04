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

from exceptions.internal_exceptions import CityNotFoundError, PrayerAlreadyExistsError, PrayerNotCreatedError
from srv.prayers.new_prayers import NewPrayers
from srv.prayers.prayers_info import PrayerMessageTextDict


@final
@attrs.define(frozen=True)
class PgNewPrayers(NewPrayers):
    """Новые записи о статусе намаза."""

    _prayer_dict: PrayerMessageTextDict
    _pgsql: Database

    # TODO #1428:30min Встроить создание намаза при запросе пользователем из namaz.today
    # TODO #1428:30min Уменьшить кол-во локальных переменных и удалить noqa комментарий
    @override
    async def create(self) -> None:  # noqa: WPS210
        """Создать."""
        city_id = await self._pgsql.fetch_val(
            'SELECT city_id FROM cities WHERE name = :name',
            {'name': self._prayer_dict['city_name']},
        )
        if not city_id:
            raise CityNotFoundError
        keys = (
            'fajr_prayer_time',
            'sunrise_prayer_time',
            'dhuhr_prayer_time',
            'asr_prayer_time',
            'magrib_prayer_time',
            'ishaa_prayer_time',
        )
        names = (
            'fajr',
            'sunrise',
            'dhuhr',
            'asr',
            'maghrib',
            "isha''a",
        )
        day = (
            datetime.datetime
            .strptime(self._prayer_dict['date'], '%d.%m.%Y')
            .astimezone(pytz.timezone('Europe/Moscow'))
        )
        try:
            await self._pgsql.execute_many(
                '\n'.join([
                    'INSERT INTO prayers',
                    '(name, time, city_id, day)',
                    'VALUES',
                    '(:name, :time, :city_id, :day)',
                    'RETURNING *',
                ]),
                [
                    {
                        'name': name,
                        'time': (
                            datetime.datetime
                            .strptime(self._prayer_dict[key], '%H:%M')  # type: ignore[literal-required]
                            .astimezone(pytz.timezone('Europe/Moscow'))
                        ),
                        'city_id': city_id,
                        'day': day,
                    }
                    for key, name in zip(keys, names, strict=True)
                ],
            )
        except UniqueViolationError as err:
            raise PrayerAlreadyExistsError from err
        created_prayers = await self._pgsql.fetch_val(
            'SELECT COUNT(*) FROM prayers WHERE city_id = :city_id AND day = :day',
            {'city_id': city_id, 'day': day},
        )
        if not created_prayers:
            raise PrayerNotCreatedError
