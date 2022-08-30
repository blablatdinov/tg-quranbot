import datetime
import uuid

from repository.prayer_time import Prayer, PrayerTimeRepository, UserPrayer


async def test_get_prayer_times_for_date(db_session, city_id, prayers, user):
    got = await PrayerTimeRepository(db_session).get_prayer_times_for_date(
        348795,
        datetime.date(2050, 4, 3),
        uuid.UUID('70d3abfd-dec6-42d1-86d0-ef98da07e813'),
    )

    assert isinstance(got, list)
    assert len(got) == 6
    assert isinstance(got[0], Prayer)


async def test_get_user_prayer_times(db_session, city_id, prayers: list[int], user, prayers_at_user):
    got = await PrayerTimeRepository(db_session).get_user_prayer_times(
        prayers,
        348795,
        datetime.date(2050, 4, 3),
    )

    assert isinstance(got, list)
    assert len(got) == 6
    assert isinstance(got[0], UserPrayer)


async def test_create_user_prayer_times(db_session, city_id, prayers: list[int], user):
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
