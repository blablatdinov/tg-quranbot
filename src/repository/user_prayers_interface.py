import datetime
from typing import Protocol

from pydantic import BaseModel


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


class UserPrayersInterface(Protocol):
    """Интерфейс времени намаза пользователя."""

    async def prayer_times(self, chat_id: int, date: datetime.date) -> list[UserPrayer]:
        """Времена намаза.

        :param chat_id: int
        :param date: datetime.date
        """
