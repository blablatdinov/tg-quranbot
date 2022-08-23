import datetime
import uuid

from repository.prayer_time import Prayer, PrayerTimeRepositoryInterface, UserPrayer


class PrayerTimeRepositoryMock(PrayerTimeRepositoryInterface):

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.date,
        city_id: int,
    ) -> list[Prayer]:
        date = datetime.datetime(2020, 1, 3)
        times = [
            datetime.time(1, 1),
            datetime.time(3, 1),
            datetime.time(11, 46),
            datetime.time(17, 34),
            datetime.time(20, 32),
            datetime.time(22, 2),
        ]
        names = ['fajr', 'sunrise', 'dhuhr', 'asr', 'magrib', "isha'a"]
        return [
            Prayer(
                id=uuid.uuid4(), city='Казань', day=date, time=time, name=name,
            )
            for time, name in zip(times, names)
        ]

    async def get_user_prayer_times(
        self,
        prayer_ids: list[int],
        chat_id: int,
        date_time: datetime.datetime,
    ) -> list[UserPrayer]:
        storage: dict[int, list[UserPrayer]] = {
            1234: [],
            111: [],
            4321: [UserPrayer(id=prayer_id, is_readed=True) for prayer_id in range(2000, 2006)],
        }
        return storage[chat_id]

    async def create_user_prayer_times(self, prayer_ids: list[int], user_id: int) -> list[UserPrayer]:
        return [
            UserPrayer(id=user_prayer_id, is_readed=True)
            for user_prayer_id in range(1000, 1006)
        ]
