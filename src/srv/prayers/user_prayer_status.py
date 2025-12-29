# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from srv.prayers.prayers_stts import PrayerStts
from srv.prayers.user_prayer_stts import UserPrayerStts


@final
@attrs.define(frozen=True)
class UserPrayerStatus(UserPrayerStts):
    """Статус прочитанности намаза."""

    _pgsql: Database

    @override
    async def change(self, prayer_status: PrayerStts) -> None:
        """Изменить статус прочитанности.

        :param prayer_status: PrayerStatus
        """
        query = '\n'.join([
            'UPDATE prayers_at_user',
            'SET is_read = :is_read',
            'WHERE prayer_at_user_id = :prayer_id',
        ])
        await self._pgsql.execute(query, {
            'is_read': prayer_status.change_to(),
            'prayer_id': prayer_status.user_prayer_id(),
        })
