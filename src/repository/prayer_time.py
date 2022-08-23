import datetime
import enum
import uuid

from databases import Database
from loguru import logger
from pydantic import BaseModel, parse_obj_as


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

    id: uuid.UUID
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


class CreatePrayerAtUserGroupQueryResult(BaseModel):
    """Результат запроса на создание группы времен намаза для пользователя."""

    id: int


class PrayerTimeRepositoryInterface(object):
    """Интерфейс для работы с временами намаза."""

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.date,
        city_id: uuid.UUID,
    ) -> list[Prayer]:
        """Получить времена намазов.

        :param chat_id: int
        :param target_datetime: datetime.datetime
        :param city_id: uuid.UUID
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
        :param date_time: datetime.date
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

    async def change_user_prayer_time_status(self, user_prayer_id: int, is_readed: bool):
        """Поменять статус прочитанности у аята.

        :param user_prayer_id: int
        :param is_readed: bool
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class PrayerTimeRepository(PrayerTimeRepositoryInterface):
    """Класс для работы с временами намаза в БД."""

    def __init__(self, connection: Database):
        self.connection = connection

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.date,
        city_id: uuid.UUID,
    ) -> list[Prayer]:
        """Получить времена намаза.

        :param chat_id: int
        :param target_datetime: datetime.datetime
        :param city_id: int
        :returns: list[Prayer]
        """
        query = """
            SELECT
                p.prayer_id AS id,
                c.name AS city,
                d.date AS day,
                p.time AS time,
                p.name AS name
            FROM prayers p
            INNER JOIN users u ON p.city_id = u.city_id
            INNER JOIN cities c ON p.city_id = c.city_id
            INNER JOIN prayer_days d ON p.day_id = d.date
            WHERE u.chat_id = :chat_id AND d.date = :date
        """
        rows = await self.connection.fetch_all(query, {'chat_id': chat_id, 'date': target_datetime})
        return parse_obj_as(list[Prayer], [row._mapping for row in rows])

    async def get_user_prayer_times(
        self,
        prayer_ids: list[uuid.UUID],
        chat_id: int,
        date: datetime.date,
    ) -> list[UserPrayer]:
        """Получить времена намазов для пользователя.

        :param prayer_ids: list[uuid.UUID]
        :param chat_id: int
        :param date: datetime.date
        :returns: list[UserPrayer]
        """
        logger.info('Search user prayer times for prayer_ids={0}, chat_id={1}, date={2}'.format(
            prayer_ids, chat_id, date,
        ))
        query_template = """
            SELECT
                up.prayer_at_user_id AS id,
                up.is_read AS is_readed
            FROM prayers_at_user up
            INNER JOIN prayers p ON up.prayer_id = p.prayer_id
            INNER JOIN prayer_days pd ON pd.date = p.day_id
            INNER JOIN users u ON up.user_id = u.chat_id
            WHERE p.prayer_id IN {0} AND u.chat_id = :chat_id AND pd.date = :date
        """
        query = query_template.format('({0})'.format(','.join(["'{0}'".format(str(x)) for x in prayer_ids])))
        rows = await self.connection.fetch_all(query, {'chat_id': chat_id, 'date': date})
        return parse_obj_as(list[UserPrayer], [row._mapping for row in rows])

    async def create_user_prayer_times(self, prayer_ids: list[uuid.UUID], user_id: int) -> list[UserPrayer]:
        """Создать времена намазов для пользователя.

        :param prayer_ids: list[uuid.UUID]
        :param user_id: int
        :returns: list[UserPrayer]
        """
        user_prayer_group_id = uuid.uuid4()
        await self.connection.execute(
            "INSERT INTO prayers_at_user_groups (prayers_at_user_group_id) VALUES (:prayers_at_user_group_id)",
            {'prayers_at_user_group_id': str(user_prayer_group_id)},
        )
        logger.info('Creating user prayers with prayer_ids={0}, user_id={1}'.format(prayer_ids, user_id))
        query = """
            INSERT INTO prayers_at_user
            (is_read, prayer_id, prayer_group_id, user_id)
            VALUES
            (:is_read, :prayer_id, :prayer_group_id, :user_id)
        """
        await self.connection.execute_many(
            query,
            [
                {'is_read': False, 'prayer_id': str(prayer_id), 'prayer_group_id': str(user_prayer_group_id), 'user_id': user_id}
                for prayer_id in prayer_ids
            ],
        )
        rows = await self.connection.fetch_all(
            "SELECT prayer_at_user_id AS id, is_read as is_readed FROM prayers_at_user WHERE prayer_group_id = :prayer_group_id",
            {'prayer_group_id': str(user_prayer_group_id)}
        )
        return parse_obj_as(list[UserPrayer], [row._mapping for row in rows])

    async def change_user_prayer_time_status(self, user_prayer_id: int, is_readed: bool):
        """Поменять статус прочитанности у аята.

        :param user_prayer_id: int
        :param is_readed: bool
        """
        query = """
            UPDATE prayers_at_user
            SET is_read = :is_read
            WHERE prayer_at_user_id = :prayer_at_user_id
        """
        await self.connection.execute(query, {'is_read': is_readed, 'prayer_at_user_id': user_prayer_id})
