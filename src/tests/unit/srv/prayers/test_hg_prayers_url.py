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
import uuid
import pytest

from srv.prayers.hg_prayers_url import HgPrayersUrl
from srv.prayers.fk_city import FkCity


class FkDb:

    async def fetch_val(self, *args, **kwargs):
        return 'https://halalguide.me/innopolis/namaz-time/'


@pytest.mark.parametrize(('month_num', 'link'), (
    (1, 'https://halalguide.me/innopolis/namaz-time/january-2025'),
    (2, 'https://halalguide.me/innopolis/namaz-time/february-2025'),
    (3, 'https://halalguide.me/innopolis/namaz-time/march-2025'),
    (4, 'https://halalguide.me/innopolis/namaz-time/april-2025'),
    (5, 'https://halalguide.me/innopolis/namaz-time/may-2025'),
    (6, 'https://halalguide.me/innopolis/namaz-time/june-2025'),
    (7, 'https://halalguide.me/innopolis/namaz-time/july-2025'),
    (8, 'https://halalguide.me/innopolis/namaz-time/august-2025'),
    (9, 'https://halalguide.me/innopolis/namaz-time/september-2025'),
    (10, 'https://halalguide.me/innopolis/namaz-time/october-2025'),
    (11, 'https://halalguide.me/innopolis/namaz-time/november-2025'),
    (12, 'https://halalguide.me/innopolis/namaz-time/december-2025'),
))
async def test_month_names(month_num, link):
    got = await HgPrayersUrl(
        FkCity(uuid.uuid4(), ''),
        FkDb(),  # type: ignore
        datetime.datetime(2025, month_num, 1).date(),
    ).to_str()

    assert got == link
