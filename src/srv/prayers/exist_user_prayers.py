# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from srv.prayers.exist_user_prayers_dict import ExistUserPrayersDict


class ExistUserPrayers(Protocol):
    """Существующие времена намаза у пользователя."""

    async def fetch(self) -> list[ExistUserPrayersDict]:
        """Получить."""
