import pytest

from services.prayers.prayer_times import PrayerStatus


@pytest.mark.parametrize('source,user_prayer_id,change_to', [
    ('mark_readed(3)', 3, True),
    ('mark_readed(40)', 40, True),
    ('mark_not_readed(9)', 9, False),
])
def test(source, user_prayer_id, change_to):
    got = PrayerStatus(source)

    assert got.user_prayer_id() == user_prayer_id
    assert got.change_to() is change_to
