import datetime
import re

import pytest

from constants import GET_PRAYER_TIMES_REGEXP
from repository.prayer_time import Prayer, PrayerTimeRepositoryInterface
from repository.user import User
from services.prayer_time import UserPrayerTimes
from tests.mocks import UserRepositoryMock


class PrayerTimeRepositoryMock(PrayerTimeRepositoryInterface):

    async def get_prayer_times_for_date(
        self,
        chat_id: int,
        target_datetime: datetime.datetime,
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
        names = ['Иртәнге', 'Восход', 'Өйлә', 'Икенде', 'Ахшам', 'Ястү']
        return [
            Prayer(
                city='Казань', day=date, time=time, name=name,
            )
            for time, name in zip(times, names)
        ]


@pytest.fixture()
def user_repository_mock():
    return UserRepositoryMock()


@pytest.fixture(autouse=True)
def user(user_repository_mock):
    user_repository_mock.storage = [
        User(
            id=1,
            is_active=True,
            day=2,
            chat_id=444,
            city_id=1,
        ),
    ]


@pytest.mark.parametrize('input_,expect', [
    ('Время намаза', True),
    ('время намаза', True),
])
def test_regex(input_, expect):
    got = re.search(GET_PRAYER_TIMES_REGEXP, input_)

    assert bool(got) is expect


async def test(user_repository_mock):
    prayers = await UserPrayerTimes(
        prayer_times_repository=PrayerTimeRepositoryMock(),
        user_repository=user_repository_mock,
        chat_id=444,
    ).get()
    answer = prayers.format_to_answer()

    assert isinstance(prayers, UserPrayerTimes)
    assert '03.01.2020' in answer.message
    assert 'Иртәнге: 01:01\n' in answer.message


# async def test_user_with_other_timezone():
#     assert False


# async def test_for_user_without_city():
#     assert False
