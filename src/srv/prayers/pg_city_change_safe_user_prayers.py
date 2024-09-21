# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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
from typing import final, override

import attrs

from srv.prayers.exist_user_prayers import ExistUserPrayers
from srv.prayers.new_prayers_at_user import NewPrayersAtUser


@final
@attrs.define(frozen=True)
class PgCityChangeSafeUserPrayers(NewPrayersAtUser):
    """Предохранитель от создания времени намаза при смене города.

    https://github.com/blablatdinov/tg-quranbot/issues/979
    """

    _origin: NewPrayersAtUser
    _exist_user_prayers: ExistUserPrayers

    @override
    async def create(self, date: datetime.date) -> None:
        """Создать.

        :param date: datetime.date
        """
        exist_user_prayers = await self._exist_user_prayers.fetch()
        prayers_count = 5
        if len(exist_user_prayers) == prayers_count:
            return
        await self._origin.create(date)
