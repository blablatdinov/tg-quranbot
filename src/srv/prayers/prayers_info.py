# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from srv.prayers.prayer_message_text_dict import PrayerMessageTextDict


class PrayersInfo(Protocol):
    """Информация о времени намаза."""

    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
