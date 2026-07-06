# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from srv.prayers.prayer_status import PrayerStatus


class UserPrayerStts(Protocol):
    """Интерфейс статуса прочитанности намаза."""

    async def change(self, prayer_status: PrayerStatus) -> None:
        """Изменить статус прочитанности.

        :param prayer_status: PrayerStatus
        """
