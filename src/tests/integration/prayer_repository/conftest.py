import datetime
import uuid

import pytest


@pytest.fixture()
async def user(db_session, city_id):
    await db_session.execute(
        "INSERT INTO users (chat_id, day, is_active, city_id) VALUES (348795, 2, 't', :city_id)",
        {'city_id': str(city_id)},
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
async def prayers(db_session, city_id, day):
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
                'prayer_id': str(prayer_id), 'time': time, 'city_id': str(city_id), 'day_id': day, 'name': name,
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
async def prayers_at_user(db_session, city_id, day, prayers: list[uuid.UUID], user):
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
