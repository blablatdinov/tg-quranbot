# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from app_types.update import Update


class Keyboard(Protocol):
    """Интерфейс клавиатуры."""

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        """
