# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
