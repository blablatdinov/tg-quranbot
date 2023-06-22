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

from exceptions.content_exceptions import UserHasNotCityIdError
from exceptions.internal_exceptions import UserHasNotGeneratedPrayersError
from exceptions.prayer_exceptions import PrayersNotFoundError, UserPrayersNotFoundError
from repository.user_prayers_interface import UserPrayer, UserPrayersInterface


@final
class PrayerNames(str, enum.Enum):  # noqa: WPS600
    """Имена намазов."""

    FAJR = 'fajr'
    SUNRISE = 'sunrise'
    DHUHR = 'dhuhr'
    ASR = 'asr'
    MAGRIB = 'magrib'
    ISHA = "isha'a"


@final
@attrs.define
class UserPrayers(UserPrayersInterface):
    """Времена намазов пользователя."""

    _connection: Database

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
                pd.date AS day,
                up.prayer_at_user_id AS id,
                up.is_read AS is_readed,
                p.time,
                p.name
            FROM prayers_at_user up
            INNER JOIN prayers p ON up.prayer_id = p.prayer_id
            INNER JOIN prayer_days pd ON pd.date = p.day_id
            INNER JOIN users u ON up.user_id = u.chat_id
            INNER JOIN cities c ON u.city_id = c.city_id
            WHERE pd.date = :date AND u.chat_id = :chat_id
            ORDER BY up.prayer_at_user_id
        """
        rows = await self._connection.fetch_all(query, {'date': date, 'chat_id': chat_id})
        prayers = [UserPrayer.parse_obj(row._mapping) for row in rows]  # noqa: WPS437
        if not prayers:
            raise UserHasNotGeneratedPrayersError
        logger.info('Prayer times taked: {0}'.format(prayers))
        return prayers


@final
@attrs.define
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
@attrs.define
class SafeNotFoundPrayers(UserPrayersInterface):
    """Времена намазов с защитой от UserPrayersNotFoundError."""

    _connection: Database
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
                INNER JOIN prayer_days pd ON pd.date = p.day_id
                WHERE pd.date = :date
            """
            prayers_count = await self._connection.fetch_val(query, {'date': date})
            if not prayers_count:
                raise PrayersNotFoundError
            query = """
                SELECT city_id FROM users WHERE chat_id = :chat_id
            """
            city_id = await self._connection.fetch_val(query, {'chat_id': chat_id})
            if not city_id:
                raise UserHasNotCityIdError
        return prayer_times


@final
@attrs.define
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
@attrs.define
class NewUserPrayers(UserPrayersInterface):
    """Объект генерирующий времена намазов пользователя."""

    _connection: Database
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
            FROM prayers p
            INNER JOIN cities c on p.city_id = c.city_id
            INNER JOIN users u on c.city_id = u.city_id
            INNER JOIN prayer_days pd on pd.date = p.day_id
            WHERE pd.date = :date AND u.chat_id = :chat_id
        """
        rows = await self._connection.fetch_all(query, {'date': date, 'chat_id': chat_id})
        if not rows:
            raise UserPrayersNotFoundError
        user_prayer_group_id = uuid.uuid4()
        await self._connection.execute(
            'INSERT INTO prayers_at_user_groups (prayers_at_user_group_id) VALUES (:prayers_at_user_group_id)',
            {'prayers_at_user_group_id': str(user_prayer_group_id)},
        )
        logger.info('Creating prayers for user <{0}>, date={1}'.format(chat_id, date))
        prayer_ids = [row._mapping['prayer_id'] for row in rows]  # noqa: WPS437
        query = """
            INSERT INTO prayers_at_user
            (is_read, prayer_id, prayer_group_id, user_id)
            VALUES
            (:is_read, :prayer_id, :prayer_group_id, :user_id)
        """
        await self._connection.execute_many(
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
