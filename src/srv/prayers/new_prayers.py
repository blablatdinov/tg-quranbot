# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class NewPrayers(Protocol):
    """Новые записи намаза."""

    async def create(self) -> None:
        """Создать.

        :param date: datetime.date
        """
