# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class SyncRunable(Protocol):
    """Интерфейс блокирующего запускаемого объекта."""

    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        """
