import datetime
import uuid

import pytest

from exceptions.content_exceptions import UserHasNotCityIdError
from repository.prayer_time import UserPrayer
from services.answers.answer import TextAnswer
from services.answers.interface import AnswerInterface
from services.prayer_time import CitySearchKeyboard, PrayerTimes, UserHasNotCityExistsSafeAnswer, UserPrayerTimes
from tests.mocks.bot import BotMock
from tests.mocks.prayer_time_repository import PrayerTimeRepositoryMock
from tests.mocks.user_repository import UserRepositoryMock


@pytest.fixture()
def user_repository_mock(user_factory):
    mock = UserRepositoryMock()
    mock.storage = [
        user_factory(1234, city_id=uuid.uuid4()),
        user_factory(4321, city_id=uuid.uuid4()),
        user_factory(111),
    ]
    return mock


async def test_generate_for_date(user_repository_mock):
    got = await UserPrayerTimes(
        await PrayerTimes(
            prayer_times_repository=PrayerTimeRepositoryMock(),
            user_repository=user_repository_mock,
            chat_id=1234,
        ).get(datetime.datetime.now()),
        datetime.datetime.now(),
    ).get_or_create_user_prayer_times()

    assert isinstance(got[0], UserPrayer)
    assert list(range(1000, 1006)) == [user_prayer.id for user_prayer in got]


async def test_get_already_exists_user_prayers(user_repository_mock):
    got = await UserPrayerTimes(
        await PrayerTimes(
            prayer_times_repository=PrayerTimeRepositoryMock(),
            user_repository=user_repository_mock,
            chat_id=4321,
        ).get(datetime.datetime.now()),
        datetime.datetime.now(),
    ).get_or_create_user_prayer_times()

    assert isinstance(got[0], UserPrayer)
    assert list(range(2000, 2006)) == [user_prayer.id for user_prayer in got]


class AnswerMock(AnswerInterface):

    async def send(self):
        raise UserHasNotCityIdError


async def test_get_prayer_time_without_city(user_repository_mock):
    got = await UserHasNotCityExistsSafeAnswer(
        AnswerMock(),
        TextAnswer(
            BotMock(),
            3284797,
            'Вы не указали город, отправьте местоположение или воспользуйтесь поиском',
            CitySearchKeyboard(),
        ),
    ).send()

    assert got[0].text == 'Вы не указали город, отправьте местоположение или воспользуйтесь поиском'
