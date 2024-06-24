from srv.prayers.prayer_status import PrayerStatus


from pyeo import elegant


from typing import Protocol


@elegant
class UserPrayerStts(Protocol):
    """Интерфейс статуса прочитанности намаза."""

    async def change(self, prayer_status: PrayerStatus) -> None:
        """Изменить статус прочитанности.

        :param prayer_status: PrayerStatus
        """