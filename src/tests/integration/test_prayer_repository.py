import datetime
import uuid

import pytest

from repository.prayer_time import Prayer, PrayerTimeRepository, UserPrayer


@pytest.fixture()
async def city(db_session):
    city_uuid = '70d3abfd-dec6-42d1-86d0-ef98da07e813'
    await db_session.execute(
        "INSERT INTO cities (city_id, name) VALUES (:city_id, 'Kazan')", {'city_id': city_uuid},
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
        'INSERT INTO prayer_days (date) VALUES (:date)', {'date': date},
    )
    return date


@pytest.fixture()
async def prayers(db_session, city, day):
    prayer_ids = [uuid.uuid4() for _ in range(6)]
    query = """
        INSERT INTO prayers
        (prayer_id, time, city_id, day_id, name)
        VALUES
        (:prayer_id, :time, :city_id, :day_id, :name)
    """
    await db_session.execute_many(
        query,
        [
            {
                'prayer_id': str(prayer_id), 'time': time, 'city_id': str(city), 'day_id': day, 'name': name,
            }
            for prayer_id, time, name in zip(
                prayer_ids,
                [
                    datetime.time(hour=1, minute=40),
                    datetime.time(hour=7, minute=43),
                    datetime.time(hour=12),
                    datetime.time(hour=17, minute=56),
                    datetime.time(hour=19, minute=1),
                    datetime.time(hour=23, minute=12),
                ],
                ['fajr', 'sunrise', 'duhr', 'asr', 'magrib', 'isha'],
            )
        ],
    )
    return prayer_ids


@pytest.fixture()
async def prayers_at_user(db_session, city, day, prayers: list[uuid.UUID], user):
    query = """
        INSERT INTO prayers_at_user_groups (prayers_at_user_group_id)
        VALUES (:prayers_at_user_group_id)
        RETURNING prayers_at_user_group_id
    """
    prayer_at_user_group_id = await db_session.fetch_val(
        query, {'prayers_at_user_group_id': str(uuid.uuid4())},
    )
    query = """
        INSERT INTO prayers_at_user (prayer_at_user_id, user_id, prayer_id, prayer_group_id, is_read)
        VALUES (:prayer_at_user_id, :user_id, :prayer_id, :prayer_group_id, :is_read)
    """
    await db_session.execute_many(
        query,
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
    await PrayerTimeRepository(db_session).change_user_prayer_time_status(
        prayers_at_user[0],
        is_readed=True,
    )

    row = await db_session.fetch_one(
        'SELECT is_read FROM prayers_at_user WHERE prayer_at_user_id = :prayer_at_user_id',
        {'prayer_at_user_id': prayers_at_user[0]},
    )

    assert row._mapping['is_read'] is True  # noqa: WPS437
