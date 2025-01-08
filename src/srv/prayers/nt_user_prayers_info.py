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
from databases import Database

from srv.prayers.pg_city import PgCity
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo
from integrations.tg.fk_chat_id import ChatId


@final
@attrs.define(frozen=True)
class NtUserPrayersInfo(PrayersInfo):
    """Декоратор для создания записи о времени намаза для пользователя."""

    _origin: PrayersInfo
    _pgsql: Database
    _chat_id: ChatId

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
        # TODO #1467:30min Написать sql запросы для вставки в таблицу prayers_at_user
        origin = await self._origin.to_dict()
        city = PgCity.name_ctor(origin['city_name'], self._pgsql)
        city_id = await city.city_id()
        day = (
            datetime.datetime
            .strptime(origin['date'], '%d.%m.%Y')
            .replace(tzinfo=pytz.timezone('Europe/Moscow'))
            .date()
        )
        # TODO #1472:30min Обработать случай если для этого города уже есть запись в таблице prayers на эту дату
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
        await PgNewPrayersAtUser(int(self._chat_id), self._pgsql).create(day)
        # prayer_ids = [
        #     row['prayer_id']
        #     for row in await self._pgsql.fetch_all(
        #         'SELECT prayer_id, name FROM prayers WHERE city_id = :city_id AND day = :day',
        #         {
        #             'city_id': str(city_id),
        #             'day': day,
        #         },
        #     )
        # ]
        # prayer_group_id = str(uuid.uuid4())
        # await self._pgsql.fetch_val(
        #     'INSERT INTO prayers_at_user_groups VALUES (:prayer_group_id)', {'prayer_group_id': prayer_group_id},
        # )
        return origin
