# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from app_types.update import Update


class Sendable(Protocol):
    """Интерфейс объекта, отправляющего ответы в API."""

    async def send(self, update: Update) -> list[dict]:
        """Отправка.

        :param update: Update
        """
