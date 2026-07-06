# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from srv.prayers.prayer_status import PrayerStatus


@pytest.mark.parametrize(('input_', 'prayer_id', 'change_to'), [
    ('mark_readed(324)', 324, True),
    ('mark_not_readed(1050)', 1050, False),
])
def test(input_, prayer_id, change_to):
    prayer_status = PrayerStatus(input_)

    assert prayer_status.user_prayer_id() == prayer_id
    assert prayer_status.change_to() is change_to
