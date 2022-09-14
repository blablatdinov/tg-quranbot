import datetime
import enum
import uuid

from databases import Database
from loguru import logger
from pydantic import BaseModel

from exceptions.internal_exceptions import UserHasNotGeneratedPrayersError


class PrayerNames(str, enum.Enum):  # noqa: WPS600
    """Имена намазов."""

    FAJR = 'fajr'
    SUNRISE = 'sunrise'
    DHUHR = 'dhuhr'
    ASR = 'asr'
    MAGRIB = 'magrib'
    ISHA = "isha'a"


class UserPrayer(BaseModel):
    """Время намаза пользователя.

    Нужна для учета прочитанных/непрочитанных намазов
    """

    id: int
    city: str
    name: str
    day: datetime.date
    time: datetime.time
    is_readed: bool


class UserPrayersInterface(object):
    """Интерфейс времени намаза пользователя."""

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Времена намаза.

        :param chat_id: int
        :param date: datetime.date
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UserPrayers(UserPrayersInterface):
    """Времена намазов пользователя."""

    def __init__(self, connection: Database):
        self._connection = connection

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
        return prayers


class SafeUserPrayers(UserPrayersInterface):
    """Времена намазов с защитой от UserHasNotGeneratedPrayersError."""

    def __init__(self, exists_user_prayers: UserPrayersInterface, new_user_prayers: UserPrayersInterface):
        self._exists_user_prayers = exists_user_prayers
        self._new_user_prayers = new_user_prayers

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


class PrayersWithoutSunrise(UserPrayersInterface):
    """Времена намазов без восхода."""

    def __init__(self, prayers: UserPrayersInterface):
        self._origin = prayers

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


class NewUserPrayers(UserPrayersInterface):
    """Объект генерирующий времена намазов пользователя."""

    def __init__(self, connection: Database, exists_user_prayers):
        self._connection = connection
        self._exists_user_prayers = exists_user_prayers

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Создать времена намазов для пользователя.

        :param chat_id: int
        :param date: datetime.date
        :returns: list[UserPrayer]
        """
        user_prayer_group_id = uuid.uuid4()
        await self._connection.execute(
            'INSERT INTO prayers_at_user_groups (prayers_at_user_group_id) VALUES (:prayers_at_user_group_id)',
            {'prayers_at_user_group_id': str(user_prayer_group_id)},
        )
        logger.info('Creating prayers for user <{0}>, date={1}'.format(chat_id, date))
        query = """
            SELECT p.prayer_id
            FROM prayers p
            INNER JOIN cities c on p.city_id = c.city_id
            INNER JOIN users u on c.city_id = u.city_id
            INNER JOIN prayer_days pd on pd.date = p.day_id
            WHERE pd.date = :date AND u.chat_id = :chat_id
        """
        rows = await self._connection.fetch_all(query, {'date': date, 'chat_id': chat_id})
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
