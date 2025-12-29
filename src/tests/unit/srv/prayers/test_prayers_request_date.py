# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime

from app_types.fk_update import FkUpdate
from srv.prayers.prayers_request_date import PrayersRequestDate


async def test_empty_update(time_machine):
    time_machine.move_to('2025-01-23')
    date = await PrayersRequestDate().parse(FkUpdate.empty_ctor())

    assert date == datetime.date(2025, 1, 23)
