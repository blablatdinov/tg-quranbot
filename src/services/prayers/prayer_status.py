from typing import Protocol

from databases import Database

from services.regular_expression import IntableRegularExpression


class PrayerStatus(object):
    """Объект, рассчитывающий данные кнопки для изменения статуса прочитанности намаза."""

    def __init__(self, source: str):
        """Конструктор класса.

        :param source: str
        """
        self._source = source

    def user_prayer_id(self) -> int:
        """Рассчитать идентификатор времени намаза пользователя.

        :return: int
        """
        return int(IntableRegularExpression(self._source))

    def change_to(self) -> bool:
        """Рассчитать статус времени намаза пользователя.

        :return: bool
        """
        return 'not' not in self._source.split('(')[0]


class UserPrayerStatusInterface(Protocol):
    """Интерфейс статуса прочитанности намаза."""

    async def change(self, prayer_status: PrayerStatus):
        """Изменить статус прочитанности.

        :param prayer_status: PrayerStatus
        """


class UserPrayerStatus(UserPrayerStatusInterface):
    """Статус прочитанности намаза."""

    def __init__(self, connection: Database):
        """Конструктор класса.

        :param connection: Database
        """
        self._connection = connection

    async def change(self, prayer_status: PrayerStatus):
        """Изменить статус прочитанности.

        :param prayer_status: PrayerStatus
        """
        query = """
            UPDATE prayers_at_user
            SET is_read = :is_read
            WHERE prayer_at_user_id = :prayer_id
        """
        await self._connection.execute(query, {
            'is_read': prayer_status.change_to(),
            'prayer_id': prayer_status.user_prayer_id(),
        })
