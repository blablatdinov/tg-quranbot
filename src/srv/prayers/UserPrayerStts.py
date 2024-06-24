from typing import Protocol

from pyeo import elegant

from srv.prayers.prayer_status import PrayerStatus


@elegant
class UserPrayerStts(Protocol):
    """Интерфейс статуса прочитанности намаза."""

    async def change(self, prayer_status: PrayerStatus) -> None:
        """Изменить статус прочитанности.

        :param prayer_status: PrayerStatus
        """
