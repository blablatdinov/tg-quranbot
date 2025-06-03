# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
