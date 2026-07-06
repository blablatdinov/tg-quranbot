# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from app_types.update import Update


class DebugParam(Protocol):
    """Интерфейс отладочной информации."""

    async def debug_value(self, update: Update) -> str:
        """Значение отладочной информации.

        :param update: Update
        """
