from repository.prayer_time import PrayerTimeRepositoryInterface
from services.prayer_time import UserPrayerTimes


class PrayerTimeRepositoryMock(PrayerTimeRepositoryInterface):
    # TODO: realize mock
    pass


async def test():
    got = await UserPrayerTimes(
        prayer_times_repository=PrayerTimeRepositoryMock(),
        chat_id=444,
    ).get()
    # TODO: insert asserts
