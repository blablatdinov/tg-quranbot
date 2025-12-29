# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime

import pytest

from srv.prayers.fk_city import FkCity
from srv.prayers.hg_prayers_url import HgPrayersUrl


# Disabled checks for stub
class FkDb:  # noqa: PEO200, FIN100

    async def fetch_val(self, *args, **kwargs):  # noqa: OVR100
        return 'https://halalguide.me/innopolis/namaz-time/'


@pytest.mark.parametrize(('month_num', 'month_name'), [
    (1, 'january'),
    (2, 'february'),
    (3, 'march'),
    (4, 'april'),
    (5, 'may'),
    (6, 'june'),
    (7, 'july'),
    (8, 'august'),
    (9, 'september'),
    (10, 'october'),
    (11, 'november'),
    (12, 'december'),
])
async def test_month_names(month_num, month_name):
    got = await HgPrayersUrl(
        FkCity.name_ctor('Innopolis'),
        FkDb(),  # type: ignore [arg-type]
        datetime.datetime(2025, month_num, 1, tzinfo=datetime.UTC).date(),
    ).to_str()

    assert got == 'https://halalguide.me/innopolis/namaz-time/{0}-2025'.format(month_name)
