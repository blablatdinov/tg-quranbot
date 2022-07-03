import datetime

import pytest

from repository.prayer_time import UserPrayer
from services.prayer_time import PrayerTimes, UserPrayerTimes
from tests.mocks import PrayerTimeRepositoryMock, UserRepositoryMock


@pytest.fixture()
def user_repository_mock(user_factory):
    mock = UserRepositoryMock()
    mock.storage = [user_factory(1234), user_factory(4321)]
    return mock


async def test_generate_for_date(user_repository_mock):
    got = await UserPrayerTimes(
        await PrayerTimes(
            prayer_times_repository=PrayerTimeRepositoryMock(),
            user_repository=user_repository_mock,
            chat_id=1234,
        ).get(),
        datetime.datetime.now(),
    ).get_or_create_user_prayer_times()

    assert isinstance(got[0], UserPrayer)
    assert [user_prayer.id for user_prayer in got] == list(range(1000, 1006))


async def test_get_already_exists_user_prayers(user_repository_mock):
    got = await UserPrayerTimes(
        await PrayerTimes(
            prayer_times_repository=PrayerTimeRepositoryMock(),
            user_repository=user_repository_mock,
            chat_id=4321,
        ).get(),
        datetime.datetime.now(),
    ).get_or_create_user_prayer_times()

    assert isinstance(got[0], UserPrayer)
    assert [user_prayer.id for user_prayer in got] == list(range(2000, 2006))
