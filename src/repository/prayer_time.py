import datetime
import enum
from dataclasses import dataclass

from pydantic import BaseModel


class PrayerNames(str, enum.Enum):  # noqa: WPS600
    """Имена намазов."""

    FAJR = 'fajr'
    SUNRISE = 'sunrise'
    DHUHR = 'dhuhr'
    ASR = 'asr'
    MAGRIB = 'magrib'
    ISHA = "isha'a"


class Prayer(BaseModel):
    """Модель времени намаза."""

    id: int
    city: str
    day: datetime.date
    time: datetime.time
    name: str


class UserPrayer(BaseModel):
    """Время намаза пользователя.

    Нужна для учета прочитанных/непрочитанных намазов
    """

    id: int
    is_readed: bool


class PrayerTimeRepositoryInterface(object):
    """Интерфейс для работы с временами намаза."""

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.datetime,
        city_id: int,
    ) -> list[Prayer]:
        """Получить времена намазов.

        :param chat_id: int
        :param target_datetime: datetime.datetime
        :param city_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_user_prayer_times(
        self,
        prayer_ids: list[int],
        chat_id: int,
        date_time: datetime.datetime,
    ) -> list[UserPrayer]:
        """Получить времена намазов для пользователя.

        :param prayer_ids: list[int]
        :param chat_id: int
        :param date_time: datetime.datetime
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def create_user_prayer_times(self, prayer_ids: list[int], user_id: int) -> list[UserPrayer]:
        """Создать времена намазов для пользователя.

        :param prayer_ids: list[int]
        :param user_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


@dataclass
class PrayerTimeRepository(PrayerTimeRepositoryInterface):
    """Класс для работы с временами намаза в БД."""

    def __init__(self, connection):
        self.connection = connection

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.datetime,
        city_id: int,
    ) -> list[Prayer]:
        """Получить времена намаза.

        :param chat_id: int
        :param target_datetime: datetime.datetime
        :param city_id: int
        :returns: list[Prayer]
        """
        query = """
            SELECT
                p.id,
                c.name as city,
                d.date as day,
                p.time as time,
                p.name as name
            FROM prayer_prayer p
            INNER JOIN bot_init_subscriber s on p.city_id = s.city_id
            INNER JOIN prayer_city c on p.city_id = c.id
            INNER JOIN prayer_day d on p.day_id = d.id
            where s.tg_chat_id = $1 and d.date = $2
        """
        rows = await self.connection.fetch(query, chat_id, target_datetime)
        return [
            Prayer(**dict(row))
            for row in rows
        ]

    async def get_user_prayer_times(
        self,
        prayer_ids: list[int],
        chat_id: int,
        date_time: datetime.datetime,
    ) -> list[UserPrayer]:
        """Получить времена намазов для пользователя.

        :param prayer_ids: list[int]
        :param chat_id: int
        :param date_time: datetime.datetime
        :returns: list[UserPrayer]
        """
        query = """
            SELECT
                up.id,
                up.is_read as is_readed
            FROM prayer_prayeratuser up
            INNER JOIN prayer_prayer p on up.prayer_id = p.id
            INNER JOIN prayer_day pd on pd.id = p.day_id
            INNER JOIN bot_init_subscriber bis on up.subscriber_id = bis.id
            where up.id IN ($3, $4, $5, $6, $7) AND bis.tg_chat_id = $1 AND pd.date = $2
        """
        rows = await self.connection.fetch(query, chat_id, date_time, *prayer_ids)
        return [
            UserPrayer(**dict(row))
            for row in rows
        ]

    async def create_user_prayer_times(self, prayer_ids: list[int], user_id: int) -> list[UserPrayer]:
        """Создать времена намазов для пользователя.

        :param prayer_ids: list[int]
        :param user_id: int
        :returns: list[UserPrayer]
        """
        query = """
            INSERT INTO prayer_prayeratusergroup (id) VALUES (default) RETURNING id
        """
        row = await self.connection.fetchrow(query)
        user_prayer_group_id = row['id']
        query = """
            WITH user_id AS (SELECT id FROM bot_init_subscriber where tg_chat_id = $1)
            INSERT INTO prayer_prayeratuser
            (is_read, prayer_id, prayer_group_id, subscriber_id)
            VALUES
            ('f', $3, $2, $1),
            ('f', $4, $2, $1),
            ('f', $5, $2, $1),
            ('f', $6, $2, $1),
            ('f', $7, $2, $1)
            RETURNING id, is_read as is_readed
        """
        rows = await self.connection.fetch(query, user_id, user_prayer_group_id, *prayer_ids)
        return [
            UserPrayer(**dict(row))
            for row in rows
        ]
