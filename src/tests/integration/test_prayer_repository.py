import datetime
import uuid

import pytest

from repository.prayer_time import PrayerTimeRepository, Prayer, UserPrayer


@pytest.fixture()
async def city(db_session):
    city_uuid = '70d3abfd-dec6-42d1-86d0-ef98da07e813'
    await db_session.execute(
        "INSERT INTO cities (city_id, name) VALUES (:city_id, 'Kazan')", {'city_id': city_uuid}
    )
    return city_uuid


@pytest.fixture()
async def user(db_session, city):
    await db_session.execute(
        "INSERT INTO users (chat_id, day, is_active, city_id) VALUES (348795, 2, 't', :city_id)", {'city_id': city},
    )
    return 348795


@pytest.fixture()
async def day(db_session):
    date = datetime.date(2050, 4, 3)
    await db_session.execute(
        "INSERT INTO prayer_days (date) VALUES (:date)", {'date': date}
    )
    return date


@pytest.fixture()
async def prayers(db_session, city, day):
    prayer_ids = [uuid.uuid4() for _ in range(6)]
    await db_session.execute_many(
        "INSERT INTO prayers (prayer_id, time, city_id, day_id, name) VALUES (:prayer_id, :time, :city_id, :day_id, :name)",
        [
            {'prayer_id': str(prayer_ids[0]), 'time': datetime.time(hour=1, minute=40), 'city_id': str(city), 'day_id': day, 'name': 'fajr'},
            {'prayer_id': str(prayer_ids[1]), 'time': datetime.time(hour=7, minute=43), 'city_id': str(city), 'day_id': day, 'name': 'sunrise'},
            {'prayer_id': str(prayer_ids[2]), 'time': datetime.time(hour=12), 'city_id': str(city), 'day_id': day, 'name': 'duhr'},
            {'prayer_id': str(prayer_ids[3]), 'time': datetime.time(hour=17, minute=56), 'city_id': str(city), 'day_id': day, 'name': 'asr'},
            {'prayer_id': str(prayer_ids[4]), 'time': datetime.time(hour=19, minute=1), 'city_id': str(city), 'day_id': day, 'name': 'magrib'},
            {'prayer_id': str(prayer_ids[5]), 'time': datetime.time(hour=23, minute=12), 'city_id': str(city), 'day_id': day, 'name': 'isha'},
        ],
    )
    return prayer_ids


@pytest.fixture()
async def prayers_at_user(db_session, city, day, prayers: list[uuid.UUID], user):
    prayer_at_user_group_id = await db_session.fetch_val(
        """INSERT INTO prayers_at_user_groups (prayers_at_user_group_id)
        VALUES (:prayers_at_user_group_id)
        RETURNING prayers_at_user_group_id""",
        {'prayers_at_user_group_id': str(uuid.uuid4())},
    )
    await db_session.execute_many(
        """INSERT INTO prayers_at_user (prayer_at_user_id, user_id, prayer_id, prayer_group_id, is_read)
        VALUES (:prayer_at_user_id, :user_id, :prayer_id, :prayer_group_id, :is_read)""",
        [
            {
                'prayer_at_user_id': prayer_at_user_id,
                'user_id': user,
                'prayer_id': str(prayer_id),
                'prayer_group_id': str(prayer_at_user_group_id),
                'is_read': False,
            }
            for prayer_at_user_id, prayer_id in zip(range(1, 7), prayers)
        ],
    )
    return list(range(1, 7))


async def test_get_prayer_times_for_date(db_session, city, prayers, user):
    got = await PrayerTimeRepository(db_session).get_prayer_times_for_date(
        348795,
        datetime.date(2050, 4, 3),
        uuid.UUID('70d3abfd-dec6-42d1-86d0-ef98da07e813'),
    )

    assert isinstance(got, list)
    assert len(got) == 6
    assert isinstance(got[0], Prayer)


async def test_get_user_prayer_times(db_session, city, prayers: list[uuid.UUID], user, prayers_at_user):
    got = await PrayerTimeRepository(db_session).get_user_prayer_times(
        prayers,
        348795,
        datetime.date(2050, 4, 3),
    )

    assert isinstance(got, list)
    assert len(got) == 6
    assert isinstance(got[0], UserPrayer)


async def test_create_user_prayer_times(db_session, city, prayers: list[uuid.UUID], user):
    got = await PrayerTimeRepository(db_session).create_user_prayer_times(
        prayers,
        348795,
    )

    assert isinstance(got, list)
    assert len(got) == 6
    assert isinstance(got[0], UserPrayer)


async def test_change_user_prayer_time_status(db_session, prayers_at_user: list[int]):
    got = await PrayerTimeRepository(db_session).change_user_prayer_time_status(
        prayers_at_user[0],
        True,
    )

    row = await db_session.fetch_one(
        'SELECT is_read FROM prayers_at_user WHERE prayer_at_user_id = :prayer_at_user_id',
        {'prayer_at_user_id': prayers_at_user[0]},
    )

    assert row._mapping['is_read'] is True


# async def test_not_found_prayers_for_date(db_session):
#     await PrayerTimeRepository(db_session).get_prayer_times_for_date


# async def test_get_user_prayer_times_without_generated_rows(db_session, city, prayers: list[uuid.UUID], user):
