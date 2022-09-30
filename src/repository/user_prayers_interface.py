import datetime

from repository.prayer_time import UserPrayer


class UserPrayersInterface(object):
    """Интерфейс времени намаза пользователя."""

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Времена намаза.

        :param chat_id: int
        :param date: datetime.date
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
