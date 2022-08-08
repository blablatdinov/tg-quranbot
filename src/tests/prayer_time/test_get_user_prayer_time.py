import datetime

import pytest

from repository.prayer_time import UserPrayer
from services.prayer_time import PrayerTimes, UserHasNotCityExistsSafeAnswer, UserPrayerTimes, UserPrayerTimesAnswer
from tests.mocks.prayer_time_repository import PrayerTimeRepositoryMock
from tests.mocks.user_repository import UserRepositoryMock


@pytest.fixture()
def user_repository_mock(user_factory):
    mock = UserRepositoryMock()
    mock.storage = [
        user_factory(1234),
        user_factory(4321),
        user_factory(111, city_id=0),
    ]
    return mock


async def test_generate_for_date(user_repository_mock):
    got = await UserPrayerTimes(
        await PrayerTimes(
            prayer_times_repository=PrayerTimeRepositoryMock(),
            user_repository=user_repository_mock,
            chat_id=1234,
        ).get(),
        datetime.datetime.now(),
        1234,
        PrayerTimeRepositoryMock(),
        user_repository_mock,
    ).get_or_create_user_prayer_times()

    assert isinstance(got[0], UserPrayer)
    assert list(range(1000, 1006)) == [user_prayer.id for user_prayer in got]


async def test_get_already_exists_user_prayers(user_repository_mock):
    got = await UserPrayerTimes(
        await PrayerTimes(
            prayer_times_repository=PrayerTimeRepositoryMock(),
            user_repository=user_repository_mock,
            chat_id=4321,
        ).get(),
        datetime.datetime.now(),
        4321,
        PrayerTimeRepositoryMock(),
        user_repository_mock,
    ).get_or_create_user_prayer_times()

    assert isinstance(got[0], UserPrayer)
    assert list(range(2000, 2006)) == [user_prayer.id for user_prayer in got]


async def test_get_prayer_time_without_city(user_repository_mock):
    got = await UserHasNotCityExistsSafeAnswer(
        UserPrayerTimesAnswer(
            UserPrayerTimes(
                PrayerTimes(
                    prayer_times_repository=PrayerTimeRepositoryMock(),
                    user_repository=user_repository_mock,
                    chat_id=111,
                ),
                datetime.datetime.now(),
                111,
                PrayerTimeRepositoryMock(),
                user_repository_mock,
            ),
        ),
    ).to_answer()

    assert got.to_list()[0].message == 'Вы не указали город, отправьте местоположение или воспользуйтесь поиском'
