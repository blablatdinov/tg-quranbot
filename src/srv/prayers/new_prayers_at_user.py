from pyeo import elegant


import datetime
from typing import Protocol


@elegant
class NewPrayersAtUser(Protocol):
    """Новые записи о статусе намаза."""

    async def create(self, date: datetime.date) -> None:
        """Создать.

        :param date: datetime.date
        """