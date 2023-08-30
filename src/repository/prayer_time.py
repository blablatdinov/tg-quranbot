"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import datetime
import enum
import uuid
from typing import final

import attrs
from databases import Database
from loguru import logger
from pyeo import elegant

from exceptions.content_exceptions import UserHasNotCityIdError
from exceptions.internal_exceptions import UserHasNotGeneratedPrayersError
from exceptions.prayer_exceptions import PrayersNotFoundError, UserPrayersNotFoundError
from repository.user_prayers_interface import UserPrayer, UserPrayersInterface


@final
@elegant
class PrayerNames(str, enum.Enum):  # noqa: WPS600
    """Имена намазов."""

    FAJR = 'fajr'
    SUNRISE = 'sunrise'
    DHUHR = 'dhuhr'
    ASR = 'asr'
    MAGRIB = 'magrib'
    ISHA = "isha'a"


@final
@attrs.define(frozen=True)
@elegant
class UserPrayers(UserPrayersInterface):
    """Времена намазов пользователя."""

    _pgsql: Database

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Времена намаза.

        :param chat_id: int
        :param date: datetime.date
        :return: list[UserPrayer]
        :raises UserHasNotGeneratedPrayersError: if user hasn't prayer times
        """
        logger.info('Getting prayer times for user <{0}>, date={1}'.format(chat_id, date))
        query = """
            SELECT
                c.name AS city,
                p.day,
                up.prayer_at_user_id AS id,
                up.is_read AS is_readed,
                p.time,
                p.name
            FROM prayers_at_user AS up
            INNER JOIN prayers AS p ON up.prayer_id = p.prayer_id
            INNER JOIN users AS u ON up.user_id = u.chat_id
            INNER JOIN cities AS c ON u.city_id = c.city_id
            WHERE p.day = :date AND u.chat_id = :chat_id
            ORDER BY up.prayer_at_user_id
        """
        rows = await self._pgsql.fetch_all(query, {'date': date, 'chat_id': chat_id})
        prayers = [
            UserPrayer(
                city=row['city'],
                day=row['day'],
                id=row['id'],
                is_readed=row['is_readed'],
                time=row['time'],
                name=row['name'],
            )
            for row in rows
        ]
        if not prayers:
            raise UserHasNotGeneratedPrayersError
        logger.info('Prayer times taked: {0}'.format(prayers))
        return prayers


@final
@attrs.define(frozen=True)
@elegant
class SafeUserPrayers(UserPrayersInterface):
    """Времена намазов с защитой от UserHasNotGeneratedPrayersError."""

    _exists_user_prayers: UserPrayersInterface
    _new_user_prayers: UserPrayersInterface

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Времена намаза.

        :param chat_id: int
        :param date: datetime.date
        :return: list[UserPrayer]
        """
        try:
            return await self._exists_user_prayers.prayer_times(chat_id, date)
        except UserHasNotGeneratedPrayersError:
            return await self._new_user_prayers.prayer_times(chat_id, date)


@final
@attrs.define(frozen=True)
@elegant
class SafeNotFoundPrayers(UserPrayersInterface):
    """Времена намазов с защитой от UserPrayersNotFoundError."""

    _pgsql: Database
    _origin: UserPrayersInterface

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Времена намаза.

        :param chat_id: int
        :param date: datetime.date
        :return: list[UserPrayer]
        :raises PrayersNotFoundError: у пользователя нет сгенерированных времен намаза
        :raises UserHasNotCityIdError: у пользователя нет города
        """
        try:
            prayer_times = await self._origin.prayer_times(chat_id, date)
        except UserPrayersNotFoundError:
            query = """
                SELECT COUNT(*) FROM prayers p
                WHERE p.day = :date
            """
            prayers_count = await self._pgsql.fetch_val(query, {'date': date})
            if not prayers_count:
                raise PrayersNotFoundError('', date)
            query = """
                SELECT city_id FROM users WHERE chat_id = :chat_id
            """
            city_id = await self._pgsql.fetch_val(query, {'chat_id': chat_id})
            if not city_id:
                raise UserHasNotCityIdError
        return prayer_times


@final
@attrs.define(frozen=True)
@elegant
class PrayersWithoutSunrise(UserPrayersInterface):
    """Времена намазов без восхода."""

    _origin: UserPrayersInterface

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Времена намаза.

        :param chat_id: int
        :param date: datetime.date
        :return: list[UserPrayer]
        """
        prayers = await self._origin.prayer_times(chat_id, date)
        return [
            prayer
            for prayer in prayers
            if prayer.name != PrayerNames.SUNRISE
        ]


@final
@attrs.define(frozen=True)
@elegant
class NewUserPrayers(UserPrayersInterface):
    """Объект генерирующий времена намазов пользователя."""

    _pgsql: Database
    _exists_user_prayers: UserPrayersInterface

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Создать времена намазов для пользователя.

        :param chat_id: int
        :param date: datetime.date
        :returns: list[UserPrayer]
        :raises UserPrayersNotFoundError: if user hasn't generated prayer times
        """
        query = """
            SELECT p.prayer_id
            FROM prayers AS p
            INNER JOIN cities AS c ON p.city_id = c.city_id
            INNER JOIN users AS u ON c.city_id = u.city_id
            WHERE p.day = :date AND u.chat_id = :chat_id
        """
        rows = await self._pgsql.fetch_all(query, {'date': date, 'chat_id': chat_id})
        if not rows:
            raise UserPrayersNotFoundError
        user_prayer_group_id = uuid.uuid4()
        await self._pgsql.execute(
            'INSERT INTO prayers_at_user_groups (prayers_at_user_group_id) VALUES (:prayers_at_user_group_id)',
            {'prayers_at_user_group_id': str(user_prayer_group_id)},
        )
        logger.info('Creating prayers for user <{0}>, date={1}'.format(chat_id, date))
        prayer_ids = [row['prayer_id'] for row in rows]
        query = """
            INSERT INTO prayers_at_user
            (is_read, prayer_id, prayer_group_id, user_id)
            VALUES
            (:is_read, :prayer_id, :prayer_group_id, :user_id)
        """
        await self._pgsql.execute_many(
            query,
            [
                {
                    'is_read': False,
                    'prayer_id': prayer_id,
                    'prayer_group_id': str(user_prayer_group_id),
                    'user_id': chat_id,
                }
                for prayer_id in prayer_ids
            ],
        )
        return await self._exists_user_prayers.prayer_times(chat_id, date)
